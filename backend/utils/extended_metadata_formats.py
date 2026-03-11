"""
Extended Metadata Format Support
Adds support for ID3, MusicBrainz, iTunes, and other industry formats
"""

import json
import xml.etree.ElementTree as ET
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone

from metadata_models import (
    MetadataFormat, ParsedMetadata, MetadataValidationError,
    ValidationSeverity, ValidationStatus
)

logger = logging.getLogger(__name__)

class ExtendedMetadataParser:
    """Parser for extended metadata formats"""
    
    def __init__(self):
        # ID3 frame mappings
        self.id3_frame_mapping = {
            'TIT2': 'title',
            'TPE1': 'artist', 
            'TALB': 'album',
            'TRCK': 'track_number',
            'TPOS': 'disc_number',
            'TYER': 'copyright_year',
            'TCON': 'genre',
            'TLEN': 'duration',
            'TCOP': 'copyright_owner',
            'TPE2': 'album_artist',
            'TPE3': 'conductor',
            'TPE4': 'remixer',
            'TPUB': 'publisher_name',
            'TCOM': 'composer_name',
            'TIT3': 'subtitle',
            'COMM': 'description',
            'USLT': 'lyrics'
        }
        
        # MusicBrainz namespaces
        self.musicbrainz_namespaces = {
            'mb': 'http://musicbrainz.org/ns/mmd-2.0#',
            'ext': 'http://musicbrainz.org/ns/ext#'
        }
        
    def parse_id3_metadata(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse ID3 tag metadata (simplified text-based format)"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            # For simplicity, assuming ID3 data is provided as JSON with frame info
            content_str = content.decode('utf-8')
            
            if content_str.strip().startswith('{'):
                # JSON format with ID3 frames
                id3_data = json.loads(content_str)
                return self._parse_id3_json(id3_data, parsed_metadata, errors)
            else:
                # Text format parsing
                return self._parse_id3_text(content_str, parsed_metadata, errors)
                
        except json.JSONDecodeError as e:
            errors.append(MetadataValidationError(
                field="id3_format",
                message=f"Invalid ID3 JSON format: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        except Exception as e:
            logger.error(f"ID3 parsing error: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"ID3 parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        parsed_metadata.validation_status = ValidationStatus.ERROR if errors else ValidationStatus.VALID
        return parsed_metadata, errors
    
    def _parse_id3_json(self, id3_data: Dict, parsed_metadata: ParsedMetadata, 
                       errors: List[MetadataValidationError]) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse ID3 data from JSON format"""
        
        try:
            # Handle frames
            frames = id3_data.get('frames', {})
            
            for frame_id, frame_value in frames.items():
                if frame_id in self.id3_frame_mapping:
                    field_name = self.id3_frame_mapping[frame_id]
                    
                    # Handle different frame types
                    if frame_id in ['TIT2', 'TPE1', 'TALB', 'TCON', 'TPUB', 'TCOM']:
                        # Text frames
                        setattr(parsed_metadata, field_name, str(frame_value))
                    elif frame_id in ['TRCK', 'TPOS']:
                        # Number frames
                        try:
                            # Handle format like "1/12"
                            if '/' in str(frame_value):
                                number = int(str(frame_value).split('/')[0])
                            else:
                                number = int(frame_value)
                            setattr(parsed_metadata, field_name, number)
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field=field_name,
                                message=f"Invalid number format in {frame_id}: {frame_value}",
                                severity=ValidationSeverity.WARNING
                            ))
                    elif frame_id == 'TYER':
                        # Year frame
                        try:
                            parsed_metadata.copyright_year = int(frame_value)
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field="copyright_year",
                                message=f"Invalid year format: {frame_value}",
                                severity=ValidationSeverity.WARNING
                            ))
                    elif frame_id == 'TLEN':
                        # Duration frame (milliseconds)
                        try:
                            duration_ms = int(frame_value)
                            minutes = duration_ms // 60000
                            seconds = (duration_ms % 60000) // 1000
                            parsed_metadata.duration = f"{minutes}:{seconds:02d}"
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field="duration",
                                message=f"Invalid duration format: {frame_value}",
                                severity=ValidationSeverity.WARNING
                            ))
            
            # Handle custom ID3 fields
            if 'custom_fields' in id3_data:
                parsed_metadata.custom_fields = id3_data['custom_fields']
            
            # Handle ISRC from TSRC frame if present
            if 'TSRC' in frames:
                parsed_metadata.isrc = frames['TSRC']
            
        except Exception as e:
            errors.append(MetadataValidationError(
                field="id3_parsing",
                message=f"Error parsing ID3 JSON: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        return parsed_metadata, errors
    
    def _parse_id3_text(self, content: str, parsed_metadata: ParsedMetadata,
                       errors: List[MetadataValidationError]) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse ID3 data from text format"""
        
        try:
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    # Map common text field names to metadata fields
                    field_mapping = {
                        'TITLE': 'title',
                        'ARTIST': 'artist',
                        'ALBUM': 'album',
                        'YEAR': 'copyright_year',
                        'GENRE': 'genre',
                        'TRACK': 'track_number',
                        'DURATION': 'duration',
                        'COMPOSER': 'composer_name',
                        'PUBLISHER': 'publisher_name',
                        'ISRC': 'isrc',
                        'COMMENT': 'description'
                    }
                    
                    if key in field_mapping:
                        field_name = field_mapping[key]
                        
                        if field_name in ['copyright_year', 'track_number']:
                            try:
                                setattr(parsed_metadata, field_name, int(value))
                            except ValueError:
                                errors.append(MetadataValidationError(
                                    field=field_name,
                                    message=f"Invalid number format: {value}",
                                    severity=ValidationSeverity.WARNING
                                ))
                        else:
                            setattr(parsed_metadata, field_name, value)
            
        except Exception as e:
            errors.append(MetadataValidationError(
                field="id3_text_parsing",
                message=f"Error parsing ID3 text: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        return parsed_metadata, errors
    
    def parse_musicbrainz_metadata(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse MusicBrainz XML metadata"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            # Parse XML
            root = ET.fromstring(content.decode('utf-8'))
            
            # Set namespaces
            ns = self.musicbrainz_namespaces
            
            # Parse recording information
            recording = root.find('.//mb:recording', ns)
            if recording is not None:
                # Title
                title_elem = recording.find('mb:title', ns)
                if title_elem is not None:
                    parsed_metadata.title = title_elem.text
                
                # Duration (in milliseconds)
                duration_elem = recording.find('mb:length', ns)
                if duration_elem is not None:
                    try:
                        duration_ms = int(duration_elem.text)
                        minutes = duration_ms // 60000
                        seconds = (duration_ms % 60000) // 1000
                        parsed_metadata.duration = f"{minutes}:{seconds:02d}"
                    except ValueError:
                        errors.append(MetadataValidationError(
                            field="duration",
                            message=f"Invalid MusicBrainz duration: {duration_elem.text}",
                            severity=ValidationSeverity.WARNING
                        ))
                
                # Artist credits
                artist_credits = recording.find('mb:artist-credit', ns)
                if artist_credits is not None:
                    artists = []
                    for name_credit in artist_credits.findall('mb:name-credit', ns):
                        artist_elem = name_credit.find('mb:artist', ns)
                        if artist_elem is not None:
                            name_elem = artist_elem.find('mb:name', ns)
                            if name_elem is not None:
                                artists.append(name_elem.text)
                    
                    if artists:
                        parsed_metadata.artist = ', '.join(artists)
                
                # ISRC
                isrcs = recording.findall('mb:isrc-list/mb:isrc', ns)
                if isrcs:
                    parsed_metadata.isrc = isrcs[0].text
            
            # Parse release information
            release = root.find('.//mb:release', ns)
            if release is not None:
                # Album title
                title_elem = release.find('mb:title', ns)
                if title_elem is not None:
                    parsed_metadata.album = title_elem.text
                
                # Release date
                date_elem = release.find('mb:date', ns)
                if date_elem is not None:
                    try:
                        parsed_metadata.release_date = datetime.fromisoformat(
                            date_elem.text.replace('Z', '+00:00')
                        )
                    except ValueError:
                        errors.append(MetadataValidationError(
                            field="release_date",
                            message=f"Invalid MusicBrainz date format: {date_elem.text}",
                            severity=ValidationSeverity.WARNING
                        ))
                
                # Barcode (UPC)
                barcode_elem = release.find('mb:barcode', ns)
                if barcode_elem is not None:
                    parsed_metadata.upc = barcode_elem.text
                
                # Label info
                label_info_list = release.find('mb:label-info-list', ns)
                if label_info_list is not None:
                    label_info = label_info_list.find('mb:label-info', ns)
                    if label_info is not None:
                        label = label_info.find('mb:label', ns)
                        if label is not None:
                            name_elem = label.find('mb:name', ns)
                            if name_elem is not None:
                                parsed_metadata.publisher_name = name_elem.text
            
            # Parse track number from medium
            medium = root.find('.//mb:medium', ns)
            if medium is not None:
                track_list = medium.find('mb:track-list', ns)
                if track_list is not None:
                    track = track_list.find('mb:track', ns)
                    if track is not None:
                        position_elem = track.find('mb:position', ns)
                        if position_elem is not None:
                            try:
                                parsed_metadata.track_number = int(position_elem.text)
                            except ValueError:
                                errors.append(MetadataValidationError(
                                    field="track_number",
                                    message=f"Invalid track position: {position_elem.text}",
                                    severity=ValidationSeverity.WARNING
                                ))
            
        except ET.ParseError as e:
            errors.append(MetadataValidationError(
                field="musicbrainz_xml",
                message=f"MusicBrainz XML parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        except Exception as e:
            logger.error(f"MusicBrainz parsing error: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"MusicBrainz parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        parsed_metadata.validation_status = ValidationStatus.ERROR if errors else ValidationStatus.VALID
        return parsed_metadata, errors
    
    def parse_itunes_metadata(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse iTunes/Apple Music metadata (plist or JSON format)"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            content_str = content.decode('utf-8')
            
            if content_str.strip().startswith('{'):
                # JSON format
                return self._parse_itunes_json(content_str, parsed_metadata, errors)
            elif '<?xml' in content_str and 'plist' in content_str:
                # Plist XML format
                return self._parse_itunes_plist(content_str, parsed_metadata, errors)
            else:
                # Simple key-value format
                return self._parse_itunes_text(content_str, parsed_metadata, errors)
                
        except Exception as e:
            logger.error(f"iTunes parsing error: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"iTunes parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        parsed_metadata.validation_status = ValidationStatus.ERROR if errors else ValidationStatus.VALID
        return parsed_metadata, errors
    
    def _parse_itunes_json(self, content: str, parsed_metadata: ParsedMetadata,
                          errors: List[MetadataValidationError]) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse iTunes JSON metadata"""
        
        try:
            itunes_data = json.loads(content)
            
            # iTunes field mapping
            field_mapping = {
                'songName': 'title',
                'artistName': 'artist',
                'collectionName': 'album',
                'trackNumber': 'track_number',
                'trackCount': 'total_tracks',
                'discNumber': 'disc_number',
                'discCount': 'total_discs',
                'releaseDate': 'release_date',
                'primaryGenreName': 'genre',
                'trackTimeMillis': 'duration',
                'copyright': 'copyright_owner',
                'description': 'description'
            }
            
            for itunes_field, metadata_field in field_mapping.items():
                if itunes_field in itunes_data:
                    value = itunes_data[itunes_field]
                    
                    if metadata_field == 'release_date':
                        try:
                            parsed_metadata.release_date = datetime.fromisoformat(
                                value.replace('Z', '+00:00')
                            )
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field="release_date",
                                message=f"Invalid iTunes release date: {value}",
                                severity=ValidationSeverity.WARNING
                            ))
                    elif metadata_field == 'duration' and isinstance(value, (int, float)):
                        # Convert milliseconds to MM:SS format
                        duration_ms = int(value)
                        minutes = duration_ms // 60000
                        seconds = (duration_ms % 60000) // 1000
                        parsed_metadata.duration = f"{minutes}:{seconds:02d}"
                    elif metadata_field in ['track_number', 'total_tracks', 'disc_number', 'total_discs']:
                        try:
                            setattr(parsed_metadata, metadata_field, int(value))
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field=metadata_field,
                                message=f"Invalid number format in iTunes {itunes_field}: {value}",
                                severity=ValidationSeverity.WARNING
                            ))
                    else:
                        setattr(parsed_metadata, metadata_field, str(value))
            
            # Handle artwork URL
            if 'artworkUrl100' in itunes_data:
                if not parsed_metadata.custom_fields:
                    parsed_metadata.custom_fields = {}
                parsed_metadata.custom_fields['artwork_url'] = itunes_data['artworkUrl100']
            
            # Handle iTunes-specific IDs
            itunes_ids = ['trackId', 'collectionId', 'artistId']
            for id_field in itunes_ids:
                if id_field in itunes_data:
                    if not parsed_metadata.custom_fields:
                        parsed_metadata.custom_fields = {}
                    parsed_metadata.custom_fields[f'itunes_{id_field}'] = itunes_data[id_field]
            
        except json.JSONDecodeError as e:
            errors.append(MetadataValidationError(
                field="itunes_json",
                message=f"Invalid iTunes JSON format: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        return parsed_metadata, errors
    
    def _parse_itunes_plist(self, content: str, parsed_metadata: ParsedMetadata,
                           errors: List[MetadataValidationError]) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse iTunes plist XML metadata"""
        
        try:
            root = ET.fromstring(content)
            
            # Find the main dictionary
            plist_dict = root.find('dict')
            if plist_dict is not None:
                # Parse key-value pairs
                keys = plist_dict.findall('key')
                values = plist_dict.findall('string') + plist_dict.findall('integer') + plist_dict.findall('date')
                
                plist_data = {}
                for i, key in enumerate(keys):
                    if i < len(values):
                        plist_data[key.text] = values[i].text
                
                # Map plist keys to metadata fields
                plist_mapping = {
                    'Name': 'title',
                    'Artist': 'artist',
                    'Album': 'album',
                    'Track Number': 'track_number',
                    'Year': 'copyright_year',
                    'Genre': 'genre',
                    'Total Time': 'duration',
                    'Comments': 'description'
                }
                
                for plist_key, metadata_field in plist_mapping.items():
                    if plist_key in plist_data:
                        value = plist_data[plist_key]
                        
                        if metadata_field in ['track_number', 'copyright_year']:
                            try:
                                setattr(parsed_metadata, metadata_field, int(value))
                            except ValueError:
                                errors.append(MetadataValidationError(
                                    field=metadata_field,
                                    message=f"Invalid number in plist {plist_key}: {value}",
                                    severity=ValidationSeverity.WARNING
                                ))
                        elif metadata_field == 'duration':
                            # iTunes stores duration in milliseconds
                            try:
                                duration_ms = int(value)
                                minutes = duration_ms // 60000
                                seconds = (duration_ms % 60000) // 1000
                                parsed_metadata.duration = f"{minutes}:{seconds:02d}"
                            except ValueError:
                                errors.append(MetadataValidationError(
                                    field="duration",
                                    message=f"Invalid duration in plist: {value}",
                                    severity=ValidationSeverity.WARNING
                                ))
                        else:
                            setattr(parsed_metadata, metadata_field, value)
            
        except ET.ParseError as e:
            errors.append(MetadataValidationError(
                field="itunes_plist",
                message=f"iTunes plist parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        return parsed_metadata, errors
    
    def _parse_itunes_text(self, content: str, parsed_metadata: ParsedMetadata,
                          errors: List[MetadataValidationError]) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse iTunes text format metadata"""
        
        try:
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Map iTunes text keys to metadata fields
                    text_mapping = {
                        'title': 'title',
                        'artist': 'artist',
                        'album': 'album',
                        'track': 'track_number',
                        'year': 'copyright_year',
                        'genre': 'genre',
                        'duration': 'duration',
                        'comment': 'description'
                    }
                    
                    key_lower = key.lower()
                    if key_lower in text_mapping:
                        field_name = text_mapping[key_lower]
                        
                        if field_name in ['track_number', 'copyright_year']:
                            try:
                                setattr(parsed_metadata, field_name, int(value))
                            except ValueError:
                                errors.append(MetadataValidationError(
                                    field=field_name,
                                    message=f"Invalid number format: {value}",
                                    severity=ValidationSeverity.WARNING
                                ))
                        else:
                            setattr(parsed_metadata, field_name, value)
            
        except Exception as e:
            errors.append(MetadataValidationError(
                field="itunes_text",
                message=f"iTunes text parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        return parsed_metadata, errors
    
    def parse_isni_metadata(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse ISNI (International Standard Name Identifier) metadata"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            content_str = content.decode('utf-8')
            
            if content_str.strip().startswith('{'):
                # JSON format
                isni_data = json.loads(content_str)
            elif '<?xml' in content_str:
                # XML format - convert to dict-like structure
                root = ET.fromstring(content_str)
                isni_data = self._xml_to_dict(root)
            else:
                # Text format
                isni_data = self._parse_isni_text(content_str)
            
            # Extract ISNI information
            if 'isni' in isni_data:
                parsed_metadata.custom_fields = {'isni': isni_data['isni']}
            
            # Map ISNI fields to metadata
            isni_mapping = {
                'name': 'artist',
                'personal_name': 'artist',
                'organization_name': 'publisher_name',
                'creation_class': 'genre',
                'title': 'title'
            }
            
            for isni_field, metadata_field in isni_mapping.items():
                if isni_field in isni_data:
                    setattr(parsed_metadata, metadata_field, isni_data[isni_field])
            
            # Handle rights information
            if 'rights' in isni_data:
                if isinstance(isni_data['rights'], list):
                    parsed_metadata.rights_holders = isni_data['rights']
                else:
                    parsed_metadata.rights_holders = [isni_data['rights']]
            
        except json.JSONDecodeError as e:
            errors.append(MetadataValidationError(
                field="isni_json",
                message=f"Invalid ISNI JSON format: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        except ET.ParseError as e:
            errors.append(MetadataValidationError(
                field="isni_xml",
                message=f"ISNI XML parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        except Exception as e:
            logger.error(f"ISNI parsing error: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"ISNI parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
        
        parsed_metadata.validation_status = ValidationStatus.ERROR if errors else ValidationStatus.VALID
        return parsed_metadata, errors
    
    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['text'] = element.text.strip()
        
        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _parse_isni_text(self, content: str) -> Dict:
        """Parse ISNI text format"""
        result = {}
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip().lower().replace(' ', '_')] = value.strip()
        
        return result