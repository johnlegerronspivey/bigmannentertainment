"""
DDEX Metadata Service - DDEX ERN/XML Generation and Validation
Handles DDEX (Digital Data Exchange) standard compliance for music industry metadata.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
import json
from content_ingestion_service import DDEXMetadata, Contributor, LicensingTerms, ContentIngestionRecord

class DDEXMessageType(str):
    NEW_RELEASE_MESSAGE = "NewReleaseMessage"
    SALES_REPORT_MESSAGE = "SalesReportMessage"
    CATALOG_LIST_MESSAGE = "CatalogListMessage"

class DDEXMetadataService:
    def __init__(self):
        self.ddex_version = "ern/41"
        self.namespace = {
            'ern': 'http://ddex.net/xml/ern/41',
            'avs': 'http://ddex.net/xml/avs/avs',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
    def generate_ddex_ern_xml(self, content_record: ContentIngestionRecord) -> str:
        """Generate DDEX ERN (Electronic Release Notification) XML"""
        
        ddex_metadata = content_record.ddex_metadata
        
        # Create root element
        root = ET.Element(
            'ern:NewReleaseMessage',
            attrib={
                'MessageSchemaVersionId': self.ddex_version,
                'BusinessProfileVersionId': 'CommonReleaseTypes/41',
                'ReleaseProfileVersionId': 'CommonReleaseTypes/41',
                'xmlns:ern': self.namespace['ern'],
                'xmlns:avs': self.namespace['avs'],
                'xmlns:xsi': self.namespace['xsi']
            }
        )
        
        # Message Header
        message_header = ET.SubElement(root, 'ern:MessageHeader')
        
        # Message Thread Id
        message_thread_id = ET.SubElement(message_header, 'ern:MessageThreadId')
        message_thread_id.text = str(uuid.uuid4())
        
        # Message Id
        message_id = ET.SubElement(message_header, 'ern:MessageId')
        message_id.text = f"BME_{content_record.content_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Message File Name
        message_filename = ET.SubElement(message_header, 'ern:MessageFileName')
        message_filename.text = f"{message_id.text}.xml"
        
        # Message Sender
        message_sender = ET.SubElement(message_header, 'ern:MessageSender')
        party_id = ET.SubElement(message_sender, 'ern:PartyId')
        party_id.text = "BigMannEntertainment"
        party_name = ET.SubElement(message_sender, 'ern:PartyName')
        trading_name = ET.SubElement(party_name, 'ern:FullName')
        trading_name.text = "Big Mann Entertainment"
        
        # Message Recipients
        for recipient in ddex_metadata.message_recipient:
            message_recipient = ET.SubElement(message_header, 'ern:MessageRecipient')
            recipient_party_id = ET.SubElement(message_recipient, 'ern:PartyId')
            recipient_party_id.text = recipient
        
        # Message Created DateTime
        message_created = ET.SubElement(message_header, 'ern:MessageCreatedDateTime')
        message_created.text = ddex_metadata.message_created.isoformat()
        
        # Message Control Type
        message_control_type = ET.SubElement(message_header, 'ern:MessageControlType')
        message_control_type.text = "LiveMessage"
        
        # Update Indicator
        update_indicator = ET.SubElement(root, 'ern:UpdateIndicator')
        update_indicator.text = "OriginalMessage"
        
        # Is Back Fill
        is_backfill = ET.SubElement(root, 'ern:IsBackfill')
        is_backfill.text = "false"
        
        # Catalog Transfer
        catalog_transfer = ET.SubElement(root, 'ern:CatalogTransfer')
        catalog_transfer.text = "false"
        
        # Release List
        release_list = ET.SubElement(root, 'ern:ReleaseList')
        release = ET.SubElement(release_list, 'ern:Release')
        
        # Release Id
        release_id_elem = ET.SubElement(release, 'ern:ReleaseId')
        grid_elem = ET.SubElement(release_id_elem, 'ern:GRid')
        grid_elem.text = ddex_metadata.grid or f"A1{str(uuid.uuid4()).replace('-', '').upper()[:18]}"
        
        if ddex_metadata.icpn:
            icpn_elem = ET.SubElement(release_id_elem, 'ern:ICPN')
            icpn_elem.text = ddex_metadata.icpn
        
        if ddex_metadata.upc:
            catalog_number = ET.SubElement(release_id_elem, 'ern:CatalogNumber')
            catalog_number.text = ddex_metadata.upc
        
        # Release Reference
        release_reference = ET.SubElement(release, 'ern:ReleaseReference')
        release_reference.text = f"R{content_record.content_id}"
        
        # Release Type
        release_type = ET.SubElement(release, 'ern:ReleaseType')
        release_type.text = ddex_metadata.release_type
        
        # Release Detail by Territory
        release_detail_by_territory = ET.SubElement(release, 'ern:ReleaseDetailsByTerritory')
        
        # Territory Code
        territory_code = ET.SubElement(release_detail_by_territory, 'ern:TerritoryCode')
        if ddex_metadata.licensing_terms and ddex_metadata.licensing_terms.territories:
            territory_code.text = ddex_metadata.licensing_terms.territories[0]
        else:
            territory_code.text = "Worldwide"
        
        # Display Artist Name
        display_artist_name = ET.SubElement(release_detail_by_territory, 'ern:DisplayArtistName')
        display_artist_name.text = ddex_metadata.main_artist
        
        # Label Name
        if ddex_metadata.label_name:
            label_name = ET.SubElement(release_detail_by_territory, 'ern:LabelName')
            label_name.text = ddex_metadata.label_name
        
        # Title
        title = ET.SubElement(release_detail_by_territory, 'ern:Title')
        title_text = ET.SubElement(title, 'ern:TitleText')
        title_text.text = ddex_metadata.title
        if ddex_metadata.subtitle:
            subtitle_text = ET.SubElement(title, 'ern:SubTitle')
            subtitle_text.text = ddex_metadata.subtitle
        
        # Display Title
        if ddex_metadata.display_title:
            display_title = ET.SubElement(release_detail_by_territory, 'ern:DisplayTitle')
            display_title.text = ddex_metadata.display_title
        
        # Genre
        for genre in ddex_metadata.genre:
            genre_elem = ET.SubElement(release_detail_by_territory, 'ern:Genre')
            genre_text = ET.SubElement(genre_elem, 'ern:GenreText')
            genre_text.text = genre
        
        # Release Date
        release_date = ET.SubElement(release_detail_by_territory, 'ern:ReleaseDate')
        release_date.text = ddex_metadata.release_date.strftime('%Y-%m-%d')
        
        # Original Release Date
        if ddex_metadata.original_release_date:
            original_release_date = ET.SubElement(release_detail_by_territory, 'ern:OriginalReleaseDate')
            original_release_date.text = ddex_metadata.original_release_date.strftime('%Y-%m-%d')
        
        # P Line
        if ddex_metadata.p_line:
            p_line = ET.SubElement(release_detail_by_territory, 'ern:PLine')
            p_line_text = ET.SubElement(p_line, 'ern:PLineText')
            p_line_text.text = ddex_metadata.p_line
            p_line_year = ET.SubElement(p_line, 'ern:Year')
            p_line_year.text = str(ddex_metadata.release_date.year)
        
        # C Line
        if ddex_metadata.c_line:
            c_line = ET.SubElement(release_detail_by_territory, 'ern:CLine')
            c_line_text = ET.SubElement(c_line, 'ern:CLineText')
            c_line_text.text = ddex_metadata.c_line
            c_line_year = ET.SubElement(c_line, 'ern:Year')
            c_line_year.text = str(ddex_metadata.release_date.year)
        
        # Parental Warning Type
        if ddex_metadata.parental_warning:
            parental_warning = ET.SubElement(release_detail_by_territory, 'ern:ParentalWarningType')
            parental_warning.text = "Explicit"
        
        # Resource Group List
        resource_group_list = ET.SubElement(release, 'ern:ResourceGroupList')
        resource_group = ET.SubElement(resource_group_list, 'ern:ResourceGroup')
        
        # Content Item
        for i, content_file in enumerate(content_record.content_files):
            resource_group_content_item = ET.SubElement(resource_group, 'ern:ResourceGroupContentItem')
            
            # Sequence Number
            sequence_number = ET.SubElement(resource_group_content_item, 'ern:SequenceNumber')
            sequence_number.text = str(i + 1)
            
            # Resource Type
            resource_type = ET.SubElement(resource_group_content_item, 'ern:ResourceType')
            if content_file.content_type.value == 'audio':
                resource_type.text = "SoundRecording"
            elif content_file.content_type.value == 'video':
                resource_type.text = "MusicalWorkVideo"
            elif content_file.content_type.value == 'image':
                resource_type.text = "Image"
            
            # Resource Reference
            resource_reference = ET.SubElement(resource_group_content_item, 'ern:ResourceReference')
            resource_reference.text = f"A{content_file.file_id}"
        
        # Resource List
        resource_list = ET.SubElement(root, 'ern:ResourceList')
        
        # Add resources for each content file
        for content_file in content_record.content_files:
            if content_file.content_type.value == 'audio':
                sound_recording = ET.SubElement(resource_list, 'ern:SoundRecording')
                self._add_audio_resource_details(sound_recording, content_file, ddex_metadata)
            elif content_file.content_type.value == 'video':
                video = ET.SubElement(resource_list, 'ern:Video')
                self._add_video_resource_details(video, content_file, ddex_metadata)
            elif content_file.content_type.value == 'image':
                image = ET.SubElement(resource_list, 'ern:Image')
                self._add_image_resource_details(image, content_file, ddex_metadata)
        
        # Deal List
        deal_list = ET.SubElement(root, 'ern:DealList')
        release_deal = ET.SubElement(deal_list, 'ern:ReleaseDeal')
        
        # Deal Reference
        deal_reference = ET.SubElement(release_deal, 'ern:DealReference')
        deal_reference.text = f"Deal_{content_record.content_id}"
        
        # Deal Terms
        deal_terms = ET.SubElement(release_deal, 'ern:DealTerms')
        
        # Commercial Model Type
        commercial_model_type = ET.SubElement(deal_terms, 'ern:CommercialModelType')
        commercial_model_type.text = ddex_metadata.commercial_model
        
        # Usage
        usage = ET.SubElement(deal_terms, 'ern:Usage')
        usage_type = ET.SubElement(usage, 'ern:UseType')
        usage_type.text = "Stream"
        
        # Territory
        territory = ET.SubElement(deal_terms, 'ern:TerritoryCode')
        territory.text = "Worldwide"
        
        # Validity Period
        validity_period = ET.SubElement(deal_terms, 'ern:ValidityPeriod')
        start_date = ET.SubElement(validity_period, 'ern:StartDate')
        start_date.text = ddex_metadata.release_date.strftime('%Y-%m-%d')
        
        # Release Reference in Deal
        deal_release_reference = ET.SubElement(release_deal, 'ern:DealReleaseReference')
        deal_release_reference.text = f"R{content_record.content_id}"
        
        # Convert to string with proper formatting
        xml_str = self._prettify_xml(root)
        return xml_str
    
    def _add_audio_resource_details(self, sound_recording_elem, content_file, ddex_metadata):
        """Add detailed information for audio resources"""
        
        # Resource Reference
        resource_reference = ET.SubElement(sound_recording_elem, 'ern:ResourceReference')
        resource_reference.text = f"A{content_file.file_id}"
        
        # Type
        type_elem = ET.SubElement(sound_recording_elem, 'ern:Type')
        type_elem.text = "MusicalWorkSoundRecording"
        
        # ISRC
        if ddex_metadata.isrc:
            isrc_elem = ET.SubElement(sound_recording_elem, 'ern:ResourceId')
            isrc = ET.SubElement(isrc_elem, 'ern:ISRC')
            isrc.text = ddex_metadata.isrc
        
        # Title
        title = ET.SubElement(sound_recording_elem, 'ern:Title')
        title_text = ET.SubElement(title, 'ern:TitleText')
        title_text.text = ddex_metadata.title
        
        # Display Artist
        display_artist = ET.SubElement(sound_recording_elem, 'ern:DisplayArtist')
        party_name = ET.SubElement(display_artist, 'ern:PartyName')
        full_name = ET.SubElement(party_name, 'ern:FullName')
        full_name.text = ddex_metadata.main_artist
        
        # Contributors
        for contributor in ddex_metadata.contributors:
            contributor_elem = ET.SubElement(sound_recording_elem, 'ern:Contributor')
            contrib_party_name = ET.SubElement(contributor_elem, 'ern:PartyName')
            contrib_full_name = ET.SubElement(contrib_party_name, 'ern:FullName')
            contrib_full_name.text = contributor.name
            
            contrib_role = ET.SubElement(contributor_elem, 'ern:Role')
            contrib_role.text = contributor.role.value.title()
        
        # Duration
        if ddex_metadata.duration:
            duration = ET.SubElement(sound_recording_elem, 'ern:Duration')
            duration.text = f"PT{ddex_metadata.duration}S"
        
        # Rights Controller
        rights_controller = ET.SubElement(sound_recording_elem, 'ern:RightsController')
        controller_party_name = ET.SubElement(rights_controller, 'ern:PartyName')
        controller_full_name = ET.SubElement(controller_party_name, 'ern:FullName')
        controller_full_name.text = ddex_metadata.master_rights_owner or "Big Mann Entertainment"
        
        # Rights Share
        rights_share = ET.SubElement(rights_controller, 'ern:RightsShare')
        rights_share.text = "100"
        
        # Technical Details
        technical_details = ET.SubElement(sound_recording_elem, 'ern:TechnicalDetails')
        
        # File
        file_elem = ET.SubElement(technical_details, 'ern:File')
        file_name = ET.SubElement(file_elem, 'ern:FileName')
        file_name.text = content_file.original_filename
        
        # File Size
        file_size = ET.SubElement(file_elem, 'ern:FileSizeInBytes')
        file_size.text = str(content_file.file_size)
        
        # Hash Sum
        hash_sum = ET.SubElement(file_elem, 'ern:HashSum')
        hash_sum_value = ET.SubElement(hash_sum, 'ern:HashSum')
        hash_sum_value.text = content_file.file_hash
        hash_sum_algorithm = ET.SubElement(hash_sum, 'ern:HashSumAlgorithmType')
        hash_sum_algorithm.text = "SHA256"
    
    def _add_video_resource_details(self, video_elem, content_file, ddex_metadata):
        """Add detailed information for video resources"""
        
        # Resource Reference
        resource_reference = ET.SubElement(video_elem, 'ern:ResourceReference')
        resource_reference.text = f"V{content_file.file_id}"
        
        # Type
        type_elem = ET.SubElement(video_elem, 'ern:Type')
        type_elem.text = "MusicalWorkVideo"
        
        # Title
        title = ET.SubElement(video_elem, 'ern:Title')
        title_text = ET.SubElement(title, 'ern:TitleText')
        title_text.text = ddex_metadata.title
        
        # Display Artist
        display_artist = ET.SubElement(video_elem, 'ern:DisplayArtist')
        party_name = ET.SubElement(display_artist, 'ern:PartyName')
        full_name = ET.SubElement(party_name, 'ern:FullName')
        full_name.text = ddex_metadata.main_artist
        
        # Duration
        if ddex_metadata.duration:
            duration = ET.SubElement(video_elem, 'ern:Duration')
            duration.text = f"PT{ddex_metadata.duration}S"
        
        # Technical Details
        technical_details = ET.SubElement(video_elem, 'ern:TechnicalDetails')
        
        # File
        file_elem = ET.SubElement(technical_details, 'ern:File')
        file_name = ET.SubElement(file_elem, 'ern:FileName')
        file_name.text = content_file.original_filename
        
        # Codec
        codec = ET.SubElement(technical_details, 'ern:CodecType')
        codec.text = content_file.technical_metadata.get('video_codec', 'H264')
    
    def _add_image_resource_details(self, image_elem, content_file, ddex_metadata):
        """Add detailed information for image resources"""
        
        # Resource Reference
        resource_reference = ET.SubElement(image_elem, 'ern:ResourceReference')
        resource_reference.text = f"I{content_file.file_id}"
        
        # Type
        type_elem = ET.SubElement(image_elem, 'ern:Type')
        type_elem.text = "FrontCoverImage"
        
        # Technical Details
        technical_details = ET.SubElement(image_elem, 'ern:TechnicalDetails')
        
        # File
        file_elem = ET.SubElement(technical_details, 'ern:File')
        file_name = ET.SubElement(file_elem, 'ern:FileName')
        file_name.text = content_file.original_filename
        
        # Image Codec Type
        image_codec = ET.SubElement(technical_details, 'ern:ImageCodecType')
        if content_file.mime_type == 'image/jpeg':
            image_codec.text = "JPEG"
        elif content_file.mime_type == 'image/png':
            image_codec.text = "PNG"
        else:
            image_codec.text = "Unknown"
    
    def _prettify_xml(self, elem):
        """Return a pretty-printed XML string for the Element"""
        rough_string = ET.tostring(elem, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def validate_ddex_xml(self, xml_content: str) -> Dict[str, Any]:
        """Validate DDEX XML against basic structure requirements"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Check for required elements
            required_elements = [
                'ern:MessageHeader',
                'ern:ReleaseList',
                'ern:ResourceList',
                'ern:DealList'
            ]
            
            for required_elem in required_elements:
                if root.find(required_elem, self.namespace) is None:
                    validation_results["errors"].append(f"Missing required element: {required_elem}")
                    validation_results["is_valid"] = False
            
            # Check message header completeness
            message_header = root.find('ern:MessageHeader', self.namespace)
            if message_header is not None:
                header_required = ['ern:MessageId', 'ern:MessageSender', 'ern:MessageCreatedDateTime']
                for header_elem in header_required:
                    if message_header.find(header_elem, self.namespace) is None:
                        validation_results["errors"].append(f"Missing message header element: {header_elem}")
                        validation_results["is_valid"] = False
            
            # Check for releases
            release_list = root.find('ern:ReleaseList', self.namespace)
            if release_list is not None:
                releases = release_list.findall('ern:Release', self.namespace)
                if len(releases) == 0:
                    validation_results["errors"].append("No releases found in ReleaseList")
                    validation_results["is_valid"] = False
                else:
                    validation_results["info"].append(f"Found {len(releases)} release(s)")
            
            # Check for resources  
            resource_list = root.find('ern:ResourceList', self.namespace)
            if resource_list is not None:
                sound_recordings = resource_list.findall('ern:SoundRecording', self.namespace)
                videos = resource_list.findall('ern:Video', self.namespace)
                images = resource_list.findall('ern:Image', self.namespace)
                
                total_resources = len(sound_recordings) + len(videos) + len(images)
                if total_resources == 0:
                    validation_results["warnings"].append("No resources found in ResourceList")
                else:
                    validation_results["info"].append(f"Found {total_resources} resource(s): {len(sound_recordings)} audio, {len(videos)} video, {len(images)} image")
            
            # Check for deals
            deal_list = root.find('ern:DealList', self.namespace)
            if deal_list is not None:
                deals = deal_list.findall('ern:ReleaseDeal', self.namespace)
                if len(deals) == 0:
                    validation_results["warnings"].append("No deals found in DealList")
                else:
                    validation_results["info"].append(f"Found {len(deals)} deal(s)")
            
        except ET.ParseError as e:
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"XML parsing error: {str(e)}")
        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def generate_catalog_list_xml(self, content_records: List[ContentIngestionRecord]) -> str:
        """Generate DDEX Catalog List XML for multiple releases"""
        
        # Create root element
        root = ET.Element(
            'ern:CatalogListMessage',
            attrib={
                'MessageSchemaVersionId': self.ddex_version,
                'BusinessProfileVersionId': 'CommonReleaseTypes/41',
                'xmlns:ern': self.namespace['ern'],
                'xmlns:avs': self.namespace['avs'],
                'xmlns:xsi': self.namespace['xsi']
            }
        )
        
        # Message Header
        message_header = ET.SubElement(root, 'ern:MessageHeader')
        
        # Message Id
        message_id = ET.SubElement(message_header, 'ern:MessageId')
        message_id.text = f"BME_CATALOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Message Sender
        message_sender = ET.SubElement(message_header, 'ern:MessageSender')
        party_id = ET.SubElement(message_sender, 'ern:PartyId')
        party_id.text = "BigMannEntertainment"
        
        # Message Created DateTime
        message_created = ET.SubElement(message_header, 'ern:MessageCreatedDateTime')
        message_created.text = datetime.now(timezone.utc).isoformat()
        
        # Catalog List
        catalog_list = ET.SubElement(root, 'ern:CatalogList')
        
        # Add each release to catalog
        for content_record in content_records:
            if content_record.distribution_ready:
                release_catalog_item = ET.SubElement(catalog_list, 'ern:ReleaseCatalogItem')
                
                # Release Reference
                release_reference = ET.SubElement(release_catalog_item, 'ern:ReleaseReference')
                release_reference.text = f"R{content_record.content_id}"
                
                # Title
                title = ET.SubElement(release_catalog_item, 'ern:Title')
                title_text = ET.SubElement(title, 'ern:TitleText')  
                title_text.text = content_record.ddex_metadata.title
                
                # Main Artist
                display_artist = ET.SubElement(release_catalog_item, 'ern:DisplayArtistName')
                display_artist.text = content_record.ddex_metadata.main_artist
                
                # Release Date
                release_date = ET.SubElement(release_catalog_item, 'ern:ReleaseDate')
                release_date.text = content_record.ddex_metadata.release_date.strftime('%Y-%m-%d')
                
                # Catalog Number
                if content_record.ddex_metadata.upc:
                    catalog_number = ET.SubElement(release_catalog_item, 'ern:CatalogNumber')
                    catalog_number.text = content_record.ddex_metadata.upc
        
        # Convert to string with proper formatting
        xml_str = self._prettify_xml(root)
        return xml_str
    
    def extract_metadata_from_xml(self, xml_content: str) -> Dict[str, Any]:
        """Extract metadata from existing DDEX XML"""
        
        try:
            root = ET.fromstring(xml_content)
            extracted_metadata = {}
            
            # Extract message information
            message_header = root.find('ern:MessageHeader', self.namespace)
            if message_header is not None:
                message_id = message_header.find('ern:MessageId', self.namespace)
                if message_id is not None:
                    extracted_metadata['message_id'] = message_id.text
            
            # Extract release information
            release_list = root.find('ern:ReleaseList', self.namespace)
            if release_list is not None:
                release = release_list.find('ern:Release', self.namespace)
                if release is not None:
                    # Extract title
                    release_details = release.find('ern:ReleaseDetailsByTerritory', self.namespace)
                    if release_details is not None:
                        title_elem = release_details.find('ern:Title', self.namespace)
                        if title_elem is not None:
                            title_text = title_elem.find('ern:TitleText', self.namespace)
                            if title_text is not None:
                                extracted_metadata['title'] = title_text.text
                        
                        # Extract artist
                        artist_elem = release_details.find('ern:DisplayArtistName', self.namespace)
                        if artist_elem is not None:
                            extracted_metadata['main_artist'] = artist_elem.text
                        
                        # Extract release date
                        release_date_elem = release_details.find('ern:ReleaseDate', self.namespace)
                        if release_date_elem is not None:
                            extracted_metadata['release_date'] = release_date_elem.text
                        
                        # Extract genres
                        genres = []
                        for genre_elem in release_details.findall('ern:Genre', self.namespace):
                            genre_text = genre_elem.find('ern:GenreText', self.namespace)
                            if genre_text is not None:
                                genres.append(genre_text.text)
                        extracted_metadata['genres'] = genres
            
            # Extract resource information
            resource_list = root.find('ern:ResourceList', self.namespace)
            if resource_list is not None:
                resources = []
                
                # Sound recordings
                for sound_recording in resource_list.findall('ern:SoundRecording', self.namespace):
                    resource_data = {'type': 'audio'}
                    
                    # ISRC
                    resource_id = sound_recording.find('ern:ResourceId', self.namespace)
                    if resource_id is not None:
                        isrc_elem = resource_id.find('ern:ISRC', self.namespace)
                        if isrc_elem is not None:
                            resource_data['isrc'] = isrc_elem.text
                    
                    # Title
                    title_elem = sound_recording.find('ern:Title', self.namespace)
                    if title_elem is not None:
                        title_text = title_elem.find('ern:TitleText', self.namespace)
                        if title_text is not None:
                            resource_data['title'] = title_text.text
                    
                    resources.append(resource_data)
                
                extracted_metadata['resources'] = resources
            
            return {
                'success': True,
                'metadata': extracted_metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }