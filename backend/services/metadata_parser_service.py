"""
Metadata Parser Service
Handles parsing of DDEX ERN (XML), MEAD, JSON, and CSV metadata formats
"""

import xml.etree.ElementTree as ET
import json
import csv
import io
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import logging
from xml.dom import minidom

from metadata_models import (
    MetadataFormat, ParsedMetadata, MetadataValidationError, 
    ValidationSeverity, ValidationStatus, DDEX_VERSIONS,
    MEADStandardFields
)
from extended_metadata_formats import ExtendedMetadataParser

logger = logging.getLogger(__name__)

class MetadataParserService:
    """Service for parsing various metadata formats"""
    
    def __init__(self):
        self.ddex_namespaces = {}
        for version, info in DDEX_VERSIONS.items():
            self.ddex_namespaces[version] = {
                'ern': info.namespace,
                'xs': 'http://www.w3.org/2001/XMLSchema'
            }
        
        # Initialize extended format parser
        self.extended_parser = ExtendedMetadataParser()
    
    def parse_metadata(self, content: bytes, file_format: MetadataFormat, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse metadata based on format"""
        errors = []
        
        try:
            if file_format == MetadataFormat.DDEX_ERN:
                return self._parse_ddex_ern(content, file_name)
            elif file_format == MetadataFormat.MEAD:
                return self._parse_mead(content, file_name)
            elif file_format == MetadataFormat.JSON:
                return self._parse_json(content, file_name)
            elif file_format == MetadataFormat.CSV:
                return self._parse_csv(content, file_name)
            elif hasattr(MetadataFormat, 'ID3') and file_format == MetadataFormat.ID3:
                return self.extended_parser.parse_id3_metadata(content, file_name)
            elif hasattr(MetadataFormat, 'MUSICBRAINZ') and file_format == MetadataFormat.MUSICBRAINZ:
                return self.extended_parser.parse_musicbrainz_metadata(content, file_name)
            elif hasattr(MetadataFormat, 'ITUNES') and file_format == MetadataFormat.ITUNES:
                return self.extended_parser.parse_itunes_metadata(content, file_name)
            elif hasattr(MetadataFormat, 'ISNI') and file_format == MetadataFormat.ISNI:
                return self.extended_parser.parse_isni_metadata(content, file_name)
            else:
                raise ValueError(f"Unsupported metadata format: {file_format}")
                
        except Exception as e:
            logger.error(f"Error parsing {file_format} metadata: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"Failed to parse {file_format} format: {str(e)}",
                severity=ValidationSeverity.ERROR,
                error_code="PARSE_ERROR"
            ))
            return ParsedMetadata(validation_status=ValidationStatus.ERROR), errors

    def _parse_ddex_ern(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse DDEX ERN XML format (multiple versions supported)"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            # Parse XML
            root = ET.fromstring(content.decode('utf-8'))
            
            # Detect DDEX version from namespace
            ddex_version = self._detect_ddex_version(root)
            parsed_metadata.ddex_version = ddex_version
            
            # Get namespace info
            if ddex_version in DDEX_VERSIONS:
                ns = self.ddex_namespaces[ddex_version]
            else:
                # Default to latest version
                ddex_version = "ern-4.4"
                ns = self.ddex_namespaces[ddex_version]
                errors.append(MetadataValidationError(
                    field="ddex_version",
                    message=f"Unknown DDEX version, defaulting to {ddex_version}",
                    severity=ValidationSeverity.WARNING
                ))
            
            # Parse message header
            message_header = root.find('.//ern:MessageHeader', ns)
            if message_header is not None:
                message_id = message_header.find('ern:MessageId', ns)
                if message_id is not None:
                    parsed_metadata.ddex_message_id = message_id.text
                
                # Get message type from root element
                parsed_metadata.ddex_message_type = root.tag.split('}')[-1] if '}' in root.tag else root.tag
            
            # Parse party information
            party_list = root.find('.//ern:PartyList', ns)
            if party_list is not None:
                parties = party_list.findall('ern:Party', ns)
                rights_holders = []
                for party in parties:
                    party_name_elem = party.find('.//ern:FullName', ns)
                    if party_name_elem is not None:
                        rights_holders.append(party_name_elem.text)
                        
                    # Get party ID
                    party_id_elem = party.find('ern:PartyId', ns)
                    if party_id_elem is not None and not parsed_metadata.party_id:
                        parsed_metadata.party_id = party_id_elem.text
                
                parsed_metadata.rights_holders = rights_holders
            
            # Parse release information
            release_list = root.find('.//ern:ReleaseList', ns)
            if release_list is not None:
                releases = release_list.findall('ern:Release', ns)
                for release in releases:
                    # Release title
                    title_elem = release.find('.//ern:TitleText', ns)
                    if title_elem is not None and not parsed_metadata.album:
                        parsed_metadata.album = title_elem.text
                    
                    # Release date
                    release_date_elem = release.find('.//ern:ReleaseDate', ns)
                    if release_date_elem is not None:
                        try:
                            parsed_metadata.release_date = datetime.fromisoformat(
                                release_date_elem.text.replace('Z', '+00:00')
                            )
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field="release_date",
                                message=f"Invalid release date format: {release_date_elem.text}",
                                severity=ValidationSeverity.WARNING
                            ))
                    
                    # UPC/EAN
                    release_id_elem = release.find('.//ern:ReleaseId[ern:Namespace="UPC"]', ns)
                    if release_id_elem is not None:
                        upc_elem = release_id_elem.find('ern:ProprietaryId', ns)
                        if upc_elem is not None:
                            parsed_metadata.upc = upc_elem.text
                    
                    # Genre
                    genre_elem = release.find('.//ern:Genre', ns)
                    if genre_elem is not None:
                        parsed_metadata.genre = genre_elem.text
            
            # Parse sound recording information  
            resource_list = root.find('.//ern:ResourceList', ns)
            if resource_list is not None:
                sound_recordings = resource_list.findall('ern:SoundRecording', ns)
                for recording in sound_recordings:
                    # Track title
                    title_elem = recording.find('.//ern:TitleText', ns)
                    if title_elem is not None and not parsed_metadata.title:
                        parsed_metadata.title = title_elem.text
                    
                    # Artist/Display Artist
                    artist_elem = recording.find('.//ern:DisplayArtistName', ns)
                    if artist_elem is not None and not parsed_metadata.artist:
                        parsed_metadata.artist = artist_elem.text
                    
                    # ISRC
                    isrc_elem = recording.find('.//ern:ISRC', ns)
                    if isrc_elem is not None:
                        parsed_metadata.isrc = isrc_elem.text
                    
                    # Duration
                    duration_elem = recording.find('.//ern:Duration', ns)
                    if duration_elem is not None:
                        parsed_metadata.duration = duration_elem.text
                    
                    # Copyright information
                    copyright_elem = recording.find('.//ern:CopyrightYear', ns)
                    if copyright_elem is not None:
                        try:
                            parsed_metadata.copyright_year = int(copyright_elem.text)
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field="copyright_year",
                                message=f"Invalid copyright year: {copyright_elem.text}",
                                severity=ValidationSeverity.WARNING
                            ))
            
            parsed_metadata.validation_status = ValidationStatus.VALID if not errors else ValidationStatus.WARNING
            
        except ET.ParseError as e:
            errors.append(MetadataValidationError(
                field="xml_structure",
                message=f"XML parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR,
                error_code="XML_PARSE_ERROR"
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        except Exception as e:
            logger.error(f"Unexpected error parsing DDEX ERN: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"Unexpected parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors
    
    def _detect_ddex_version(self, root: ET.Element) -> str:
        """Detect DDEX version from XML namespace"""
        # Check root element namespace
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0][1:]  # Remove { and }
            
            # Match namespace to known versions
            for version, info in DDEX_VERSIONS.items():
                if namespace == info.namespace:
                    return version
            
            # Try to extract version from namespace URL
            if 'ern' in namespace:
                version_match = re.search(r'ern[/\\](\d+)', namespace)
                if version_match:
                    version_num = version_match.group(1)
                    if len(version_num) == 2:  # e.g., "44" -> "ern-4.4"
                        return f"ern-{version_num[0]}.{version_num[1]}"
        
        # Default to latest version if not detected
        return "ern-4.4"
    
    def _parse_mead(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse MEAD (Music and Entertainment Asset Database) format"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            # MEAD can be JSON or XML format
            content_str = content.decode('utf-8').strip()
            
            if content_str.startswith('{') or content_str.startswith('['):
                # JSON format MEAD
                return self._parse_mead_json(content_str, parsed_metadata, errors)
            elif content_str.startswith('<'):
                # XML format MEAD
                return self._parse_mead_xml(content_str, parsed_metadata, errors)
            else:
                # Assume CSV format MEAD
                return self._parse_mead_csv(content_str, parsed_metadata, errors)
                
        except Exception as e:
            logger.error(f"Error parsing MEAD format: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"MEAD parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors
    
    def _parse_mead_json(self, content: str, parsed_metadata: ParsedMetadata, errors: List) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse MEAD JSON format"""
        try:
            mead_data = json.loads(content)
            
            # Handle both single object and array
            if isinstance(mead_data, list) and mead_data:
                mead_data = mead_data[0]  # Take first record
            
            # Map MEAD fields to parsed metadata
            field_mapping = {
                'title': 'title',
                'version_title': 'title',
                'artist_name': 'artist', 
                'album_title': 'album',
                'isrc': 'isrc',
                'upc': 'upc',
                'release_date': 'release_date',
                'rights_holder': 'rights_holders',
                'label_name': 'publisher_name',
                'genre': 'genre',
                'track_duration': 'duration'
            }
            
            for mead_field, metadata_field in field_mapping.items():
                if mead_field in mead_data and mead_data[mead_field]:
                    value = mead_data[mead_field]
                    
                    if metadata_field == 'rights_holders':
                        parsed_metadata.rights_holders = [value] if isinstance(value, str) else value
                    elif metadata_field == 'release_date':
                        try:
                            parsed_metadata.release_date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except ValueError:
                            errors.append(MetadataValidationError(
                                field="release_date",
                                message=f"Invalid MEAD release date format: {value}",
                                severity=ValidationSeverity.WARNING
                            ))
                    else:
                        setattr(parsed_metadata, metadata_field, value)
            
            parsed_metadata.validation_status = ValidationStatus.VALID if not errors else ValidationStatus.WARNING
            
        except json.JSONDecodeError as e:
            errors.append(MetadataValidationError(
                field="json_format",
                message=f"Invalid MEAD JSON format: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors
    
    def _parse_mead_xml(self, content: str, parsed_metadata: ParsedMetadata, errors: List) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse MEAD XML format"""
        try:
            root = ET.fromstring(content)
            
            # MEAD XML field mapping
            field_xpath_mapping = {
                'title': ['.//title', './/version_title'],
                'artist': ['.//artist_name', './/performer'],
                'album': ['.//album_title', './/release_title'], 
                'isrc': ['.//isrc', './/ISRC'],
                'upc': ['.//upc', './/UPC'],
                'genre': ['.//genre'],
                'duration': ['.//track_duration', './/duration']
            }
            
            for field, xpaths in field_xpath_mapping.items():
                for xpath in xpaths:
                    element = root.find(xpath)
                    if element is not None and element.text:
                        setattr(parsed_metadata, field, element.text)
                        break
            
            # Rights holders (can be multiple)
            rights_elements = root.findall('.//rights_holder') + root.findall('.//rightsholder')
            if rights_elements:
                parsed_metadata.rights_holders = [elem.text for elem in rights_elements if elem.text]
            
            # Release date
            release_date_elem = root.find('.//release_date')
            if release_date_elem is not None and release_date_elem.text:
                try:
                    parsed_metadata.release_date = datetime.fromisoformat(
                        release_date_elem.text.replace('Z', '+00:00')
                    )
                except ValueError:
                    errors.append(MetadataValidationError(
                        field="release_date",
                        message=f"Invalid MEAD XML release date format: {release_date_elem.text}",
                        severity=ValidationSeverity.WARNING
                    ))
            
            parsed_metadata.validation_status = ValidationStatus.VALID if not errors else ValidationStatus.WARNING
            
        except ET.ParseError as e:
            errors.append(MetadataValidationError(
                field="xml_structure", 
                message=f"MEAD XML parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors
    
    def _parse_mead_csv(self, content: str, parsed_metadata: ParsedMetadata, errors: List) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse MEAD CSV format"""
        try:
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Take first row for single track metadata
            for row in csv_reader:
                # MEAD CSV field mapping (case-insensitive)
                field_mapping = {
                    'title': ['title', 'track_title', 'version_title'],
                    'artist': ['artist_name', 'artist', 'performer'],
                    'album': ['album_title', 'album', 'release_title'],
                    'isrc': ['isrc', 'ISRC'],
                    'upc': ['upc', 'UPC', 'ean'],
                    'genre': ['genre', 'primary_genre'],
                    'duration': ['track_duration', 'duration']
                }
                
                # Normalize column names
                row_normalized = {k.lower().replace(' ', '_'): v for k, v in row.items()}
                
                for field, possible_columns in field_mapping.items():
                    for col in possible_columns:
                        if col.lower() in row_normalized and row_normalized[col.lower()]:
                            setattr(parsed_metadata, field, row_normalized[col.lower()])
                            break
                
                # Rights holders
                rights_cols = ['rights_holder', 'rightsholder', 'copyright_owner']
                for col in rights_cols:
                    if col in row_normalized and row_normalized[col]:
                        parsed_metadata.rights_holders = [row_normalized[col]]
                        break
                
                # Release date
                date_cols = ['release_date', 'releasedate', 'date']
                for col in date_cols:
                    if col in row_normalized and row_normalized[col]:
                        try:
                            parsed_metadata.release_date = datetime.fromisoformat(
                                row_normalized[col].replace('Z', '+00:00')
                            )
                        except ValueError:
                            try:
                                # Try common date formats
                                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                                    parsed_metadata.release_date = datetime.strptime(
                                        row_normalized[col], fmt
                                    ).replace(tzinfo=timezone.utc)
                                    break
                            except ValueError:
                                errors.append(MetadataValidationError(
                                    field="release_date",
                                    message=f"Invalid MEAD CSV date format: {row_normalized[col]}",
                                    severity=ValidationSeverity.WARNING
                                ))
                        break
                
                break  # Only process first row for single metadata
            
            parsed_metadata.validation_status = ValidationStatus.VALID if not errors else ValidationStatus.WARNING
            
        except Exception as e:
            errors.append(MetadataValidationError(
                field="csv_format",
                message=f"MEAD CSV parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors
    
    def _parse_json(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse standard JSON metadata format"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            json_data = json.loads(content.decode('utf-8'))
            
            # Handle array of metadata objects
            if isinstance(json_data, list) and json_data:
                json_data = json_data[0]  # Take first record
            
            # Direct field mapping for JSON
            direct_fields = [
                'title', 'artist', 'album', 'isrc', 'upc', 'ean',
                'publisher_name', 'composer_name', 'copyright_owner',
                'copyright_year', 'genre', 'sub_genre', 'language',
                'duration', 'track_number', 'total_tracks',
                'description'
            ]
            
            for field in direct_fields:
                if field in json_data and json_data[field]:
                    setattr(parsed_metadata, field, json_data[field])
            
            # Handle arrays
            if 'rights_holders' in json_data:
                parsed_metadata.rights_holders = json_data['rights_holders'] if isinstance(
                    json_data['rights_holders'], list
                ) else [json_data['rights_holders']]
            
            if 'tags' in json_data:
                parsed_metadata.tags = json_data['tags'] if isinstance(
                    json_data['tags'], list
                ) else [tag.strip() for tag in json_data['tags'].split(',')]
            
            # Handle dates
            date_fields = ['release_date', 'original_release_date']
            for date_field in date_fields:
                if date_field in json_data and json_data[date_field]:
                    try:
                        parsed_date = datetime.fromisoformat(
                            json_data[date_field].replace('Z', '+00:00')
                        )
                        setattr(parsed_metadata, date_field, parsed_date)
                    except ValueError:
                        errors.append(MetadataValidationError(
                            field=date_field,
                            message=f"Invalid JSON date format: {json_data[date_field]}",
                            severity=ValidationSeverity.WARNING
                        ))
            
            # Custom fields
            excluded_fields = set(direct_fields + date_fields + ['rights_holders', 'tags'])
            custom_fields = {k: v for k, v in json_data.items() if k not in excluded_fields}
            if custom_fields:
                parsed_metadata.custom_fields = custom_fields
            
            parsed_metadata.validation_status = ValidationStatus.VALID if not errors else ValidationStatus.WARNING
            
        except json.JSONDecodeError as e:
            errors.append(MetadataValidationError(
                field="json_format",
                message=f"Invalid JSON format: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {str(e)}")
            errors.append(MetadataValidationError(
                field="general",
                message=f"JSON parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors
    
    def _parse_csv(self, content: bytes, file_name: str) -> Tuple[ParsedMetadata, List[MetadataValidationError]]:
        """Parse CSV metadata format"""
        errors = []
        parsed_metadata = ParsedMetadata()
        
        try:
            content_str = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content_str))
            
            # Process first row
            for row in csv_reader:
                # Normalize column names (lowercase, replace spaces with underscores)
                row_normalized = {k.lower().replace(' ', '_').replace('-', '_'): v 
                                for k, v in row.items() if v}
                
                # CSV field mapping with multiple possible column names
                field_mapping = {
                    'title': ['title', 'track_title', 'song_title', 'track_name'],
                    'artist': ['artist', 'artist_name', 'performer', 'primary_artist'],
                    'album': ['album', 'album_title', 'release_title', 'album_name'],
                    'isrc': ['isrc', 'track_isrc'],
                    'upc': ['upc', 'album_upc', 'ean', 'barcode'],
                    'genre': ['genre', 'primary_genre', 'music_genre'],
                    'publisher_name': ['publisher', 'publisher_name', 'publishing_company'],
                    'composer_name': ['composer', 'composer_name', 'songwriter'],
                    'copyright_year': ['copyright_year', 'p_year', '(p)_year', 'year'],
                    'duration': ['duration', 'track_duration', 'length', 'runtime'],
                    'track_number': ['track_number', 'track_no', 'position'],
                    'description': ['description', 'notes', 'comments']
                }
                
                for field, possible_columns in field_mapping.items():
                    for col in possible_columns:
                        if col in row_normalized:
                            value = row_normalized[col]
                            if field == 'copyright_year':
                                try:
                                    setattr(parsed_metadata, field, int(value))
                                except ValueError:
                                    errors.append(MetadataValidationError(
                                        field=field,
                                        message=f"Invalid copyright year: {value}",
                                        severity=ValidationSeverity.WARNING
                                    ))
                            elif field == 'track_number':
                                try:
                                    setattr(parsed_metadata, field, int(value))
                                except ValueError:
                                    errors.append(MetadataValidationError(
                                        field=field,
                                        message=f"Invalid track number: {value}",
                                        severity=ValidationSeverity.WARNING
                                    ))
                            else:
                                setattr(parsed_metadata, field, value)
                            break
                
                # Rights holders (multiple columns possible)
                rights_columns = ['rights_holders', 'rights_holder', 'copyright_owner', 'label']
                rights_values = []
                for col in rights_columns:
                    if col in row_normalized and row_normalized[col]:
                        # Split by comma if multiple values
                        values = [v.strip() for v in row_normalized[col].split(',')]
                        rights_values.extend(values)
                
                if rights_values:
                    parsed_metadata.rights_holders = list(set(rights_values))  # Remove duplicates
                
                # Release date with multiple formats
                date_columns = ['release_date', 'releasedate', 'date', 'publish_date']
                for col in date_columns:
                    if col in row_normalized and row_normalized[col]:
                        date_value = row_normalized[col]
                        try:
                            # Try ISO format first
                            parsed_metadata.release_date = datetime.fromisoformat(
                                date_value.replace('Z', '+00:00')
                            )
                            break
                        except ValueError:
                            # Try common formats
                            date_formats = [
                                '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', 
                                '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S'
                            ]
                            for fmt in date_formats:
                                try:
                                    parsed_metadata.release_date = datetime.strptime(
                                        date_value, fmt
                                    ).replace(tzinfo=timezone.utc)
                                    break
                                except ValueError:
                                    continue
                            else:
                                errors.append(MetadataValidationError(
                                    field="release_date",
                                    message=f"Invalid CSV date format: {date_value}",
                                    severity=ValidationSeverity.WARNING,
                                    suggested_fix="Use format: YYYY-MM-DD"
                                ))
                        break
                
                # Tags
                tag_columns = ['tags', 'keywords', 'categories']
                for col in tag_columns:
                    if col in row_normalized and row_normalized[col]:
                        tags = [tag.strip() for tag in row_normalized[col].split(',')]
                        parsed_metadata.tags = tags
                        break
                
                break  # Only process first row
            
            parsed_metadata.validation_status = ValidationStatus.VALID if not errors else ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            errors.append(MetadataValidationError(
                field="csv_format",
                message=f"CSV parsing error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))
            parsed_metadata.validation_status = ValidationStatus.ERROR
            
        return parsed_metadata, errors