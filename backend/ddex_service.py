import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import os
from ddex_models import *

class DDEXService:
    def __init__(self):
        self.namespace_map = {
            'ern': 'http://ddex.net/xml/ern/41',
            'dsr': 'http://ddex.net/xml/dsr/41', 
            'cwr': 'http://ddex.net/xml/cwr/30',
            'mwn': 'http://ddex.net/xml/mwn/41'
        }
        
    def generate_ern_xml(self, message: DDEXMessage) -> str:
        """Generate Electronic Release Notification XML"""
        if not message.release:
            raise ValueError("Release information required for ERN message")
            
        # Create root element with namespaces
        root = ET.Element(
            f"{{{self.namespace_map['ern']}}}NewReleaseMessage",
            attrib={
                "MessageSchemaVersionId": message.schema_version_id,
                "BusinessProfileVersionId": message.business_profile_type,
                "ReleaseProfileVersionId": "CommonReleaseTypes/14",
                "LanguageAndScriptCode": "en"
            }
        )
        
        # Add namespace declarations
        root.set("xmlns", self.namespace_map['ern'])
        
        # Message Header
        header = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}MessageHeader")
        
        message_thread_id = ET.SubElement(header, f"{{{self.namespace_map['ern']}}}MessageThreadId")
        message_thread_id.text = message.message_id
        
        message_id = ET.SubElement(header, f"{{{self.namespace_map['ern']}}}MessageId")
        message_id.text = message.message_id
        
        message_filename = ET.SubElement(header, f"{{{self.namespace_map['ern']}}}MessageFileName")
        message_filename.text = f"{message.message_id}.xml"
        
        message_sender = ET.SubElement(header, f"{{{self.namespace_map['ern']}}}MessageSender")
        party_id = ET.SubElement(message_sender, f"{{{self.namespace_map['ern']}}}PartyId")
        party_id.text = message.sender_id
        party_name = ET.SubElement(message_sender, f"{{{self.namespace_map['ern']}}}PartyName")
        party_name.text = message.sender_name
        
        if message.recipient_id:
            message_recipient = ET.SubElement(header, f"{{{self.namespace_map['ern']}}}MessageRecipient")
            recipient_party_id = ET.SubElement(message_recipient, f"{{{self.namespace_map['ern']}}}PartyId")
            recipient_party_id.text = message.recipient_id
            if message.recipient_name:
                recipient_party_name = ET.SubElement(message_recipient, f"{{{self.namespace_map['ern']}}}PartyName")
                recipient_party_name.text = message.recipient_name
        
        message_created = ET.SubElement(header, f"{{{self.namespace_map['ern']}}}MessageCreatedDateTime")
        message_created.text = message.created_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Update Indicator
        update_indicator = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}UpdateIndicator")
        update_indicator.text = "OriginalMessage"
        
        # Is Backfill
        is_backfill = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}IsBackfill")
        is_backfill.text = "false"
        
        # CatalogTransfer (Optional)
        catalog_transfer = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}CatalogTransfer")
        catalog_transfer.text = "false"
        
        # Resource List
        resource_list = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}ResourceList")
        
        for resource in message.release.resources:
            self._add_resource_to_ern(resource_list, resource)
            
        # Release List  
        release_list = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}ReleaseList")
        self._add_release_to_ern(release_list, message.release)
        
        # Deal List
        deal_list = ET.SubElement(root, f"{{{self.namespace_map['ern']}}}DealList")
        self._add_deal_to_ern(deal_list, message.release, message.deals)
        
        return self._prettify_xml(root)
    
    def _add_resource_to_ern(self, resource_list: ET.Element, resource: DDEXResource):
        """Add resource (sound recording, video, etc.) to ERN XML"""
        if resource.resource_type == "SoundRecording":
            sound_recording = ET.SubElement(resource_list, f"{{{self.namespace_map['ern']}}}SoundRecording")
            
            # Resource reference
            resource_reference = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}ResourceReference")
            resource_reference.text = resource.resource_id
            
            # Type
            resource_type = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}Type")
            resource_type.text = "SoundRecording"
            
            # Resource ID
            resource_id = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}ResourceId")
            isrc_elem = ET.SubElement(resource_id, f"{{{self.namespace_map['ern']}}}ISRC")
            isrc_elem.text = resource.isrc or f"BME{datetime.now().strftime('%y')}{uuid.uuid4().hex[:6].upper()}"
            
            # Reference title
            reference_title = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}ReferenceTitle")
            title_text = ET.SubElement(reference_title, f"{{{self.namespace_map['ern']}}}TitleText")
            title_text.text = resource.title
            
            # Duration
            if resource.duration:
                duration = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}Duration")
                duration.text = resource.duration
                
            # Artists and contributors
            for artist in resource.artists:
                display_artist = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}DisplayArtist")
                party_name = ET.SubElement(display_artist, f"{{{self.namespace_map['ern']}}}PartyName")
                party_name.text = artist.party_name
                
                artist_role = ET.SubElement(display_artist, f"{{{self.namespace_map['ern']}}}ArtistRole")
                artist_role.text = "MainArtist"
                
            # Technical details
            technical_details = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}TechnicalDetails")
            technical_resource_details = ET.SubElement(technical_details, f"{{{self.namespace_map['ern']}}}TechnicalResourceDetails")
            
            audio_codec_type = ET.SubElement(technical_resource_details, f"{{{self.namespace_map['ern']}}}AudioCodecType")
            audio_codec_type.text = "MP3" if "mp3" in resource.mime_type.lower() else "Unknown"
            
            if resource.bitrate:
                bitrate = ET.SubElement(technical_resource_details, f"{{{self.namespace_map['ern']}}}BitRate")
                bitrate.text = str(resource.bitrate)
                
            if resource.sample_rate:
                sample_rate = ET.SubElement(technical_resource_details, f"{{{self.namespace_map['ern']}}}SamplingRate")
                sample_rate.text = str(resource.sample_rate)
                
            # File
            file_elem = ET.SubElement(technical_resource_details, f"{{{self.namespace_map['ern']}}}File")
            uri = ET.SubElement(file_elem, f"{{{self.namespace_map['ern']}}}URI")
            uri.text = os.path.basename(resource.file_path)
            
            # Parental warning
            parental_warning = ET.SubElement(sound_recording, f"{{{self.namespace_map['ern']}}}ParentalWarningType")
            parental_warning.text = resource.parental_warning_type or "NotExplicit"
            
        elif resource.resource_type == "Image":
            image = ET.SubElement(resource_list, f"{{{self.namespace_map['ern']}}}Image")
            
            resource_reference = ET.SubElement(image, f"{{{self.namespace_map['ern']}}}ResourceReference")
            resource_reference.text = resource.resource_id
            
            image_type = ET.SubElement(image, f"{{{self.namespace_map['ern']}}}Type")
            image_type.text = "FrontCoverImage"
            
            # Technical details for image
            technical_details = ET.SubElement(image, f"{{{self.namespace_map['ern']}}}TechnicalDetails")
            technical_image_details = ET.SubElement(technical_details, f"{{{self.namespace_map['ern']}}}TechnicalResourceDetails")
            
            file_elem = ET.SubElement(technical_image_details, f"{{{self.namespace_map['ern']}}}File")
            uri = ET.SubElement(file_elem, f"{{{self.namespace_map['ern']}}}URI")
            uri.text = os.path.basename(resource.file_path)
    
    def _add_release_to_ern(self, release_list: ET.Element, release: DDEXRelease):
        """Add release information to ERN XML"""
        release_elem = ET.SubElement(release_list, f"{{{self.namespace_map['ern']}}}Release")
        
        # Release reference
        release_reference = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}ReleaseReference")
        release_reference.text = release.release_id
        
        # Release type
        release_type = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}ReleaseType")
        release_type.text = release.release_type.value
        
        # Release ID
        release_id = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}ReleaseId")
        
        if release.grid:
            grid = ET.SubElement(release_id, f"{{{self.namespace_map['ern']}}}GRid")
            grid.text = release.grid
        
        if release.icpn:
            icpn = ET.SubElement(release_id, f"{{{self.namespace_map['ern']}}}ICPN")
            icpn.text = release.icpn
            
        if release.catalog_number:
            catalog_number = ET.SubElement(release_id, f"{{{self.namespace_map['ern']}}}CatalogNumber")
            namespace = ET.SubElement(catalog_number, f"{{{self.namespace_map['ern']}}}Namespace")
            namespace.text = release.label_name
            value = ET.SubElement(catalog_number, f"{{{self.namespace_map['ern']}}}Value")
            value.text = release.catalog_number
        
        # Reference title
        reference_title = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}ReferenceTitle")
        title_text = ET.SubElement(reference_title, f"{{{self.namespace_map['ern']}}}TitleText")
        title_text.text = release.title
        
        # Display artist
        display_artist = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}DisplayArtist")
        party_name = ET.SubElement(display_artist, f"{{{self.namespace_map['ern']}}}PartyName")
        party_name.text = release.display_artist
        artist_role = ET.SubElement(display_artist, f"{{{self.namespace_map['ern']}}}ArtistRole")
        artist_role.text = "MainArtist"
        
        # Label name
        marketing_label = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}MarketingLabel")
        label_name = ET.SubElement(marketing_label, f"{{{self.namespace_map['ern']}}}LabelName")
        label_name.text = release.label_name
        
        # Resource/track references
        for i, resource in enumerate(release.resources):
            resource_group = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}ResourceGroup")
            resource_group_content_item = ET.SubElement(resource_group, f"{{{self.namespace_map['ern']}}}ResourceGroupContentItem")
            sequence_number = ET.SubElement(resource_group_content_item, f"{{{self.namespace_map['ern']}}}SequenceNumber")
            sequence_number.text = str(i + 1)
            resource_ref = ET.SubElement(resource_group_content_item, f"{{{self.namespace_map['ern']}}}ResourceReference")
            resource_ref.text = resource.resource_id
        
        # Release date
        release_date = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}ReleaseDate")
        release_date.text = release.release_date.strftime("%Y-%m-%d")
        
        # Original release date
        if release.original_release_date:
            original_release_date = ET.SubElement(release_elem, f"{{{self.namespace_map['ern']}}}OriginalReleaseDate")
            original_release_date.text = release.original_release_date.strftime("%Y-%m-%d")
    
    def _add_deal_to_ern(self, deal_list: ET.Element, release: DDEXRelease, deals: List[Dict[str, Any]]):
        """Add commercial terms (deal) to ERN XML"""
        release_deal = ET.SubElement(deal_list, f"{{{self.namespace_map['ern']}}}ReleaseDeal")
        
        # Deal reference
        deal_reference = ET.SubElement(release_deal, f"{{{self.namespace_map['ern']}}}DealReference")
        deal_reference.text = f"DEAL_{release.release_id}"
        
        # Deal terms
        deal_terms = ET.SubElement(release_deal, f"{{{self.namespace_map['ern']}}}DealTerms")
        
        # Commercial model type
        commercial_model_type = ET.SubElement(deal_terms, f"{{{self.namespace_map['ern']}}}CommercialModelType")
        commercial_model_type.text = "SubscriptionModel"
        
        # Usage type
        usage = ET.SubElement(deal_terms, f"{{{self.namespace_map['ern']}}}Usage")
        use_type = ET.SubElement(usage, f"{{{self.namespace_map['ern']}}}UseType")
        use_type.text = "OnDemandStream"
        
        # Territory
        territory_code = ET.SubElement(deal_terms, f"{{{self.namespace_map['ern']}}}TerritoryCode")
        territory_code.text = "Worldwide"
        
        # Valid from/until
        validity_period = ET.SubElement(deal_terms, f"{{{self.namespace_map['ern']}}}ValidityPeriod")
        start_date = ET.SubElement(validity_period, f"{{{self.namespace_map['ern']}}}StartDate")
        start_date.text = release.release_date.strftime("%Y-%m-%d")
        
        # Rights granted
        for right in release.rights_granted:
            use_type_elem = ET.SubElement(usage, f"{{{self.namespace_map['ern']}}}UseType")
            use_type_elem.text = right.value
        
        # Release reference in deal
        deal_release_reference = ET.SubElement(release_deal, f"{{{self.namespace_map['ern']}}}DealReleaseReference")
        deal_release_reference.text = release.release_id
    
    def generate_cwr_xml(self, work_registration: DDEXWorkRegistration) -> str:
        """Generate Common Works Registration XML"""
        root = ET.Element(
            f"{{{self.namespace_map['cwr']}}}CWRMessage",
            attrib={
                "MessageSchemaVersionId": "30",
                "LanguageAndScriptCode": "en"
            }
        )
        
        # Add namespace
        root.set("xmlns", self.namespace_map['cwr'])
        
        # Message Header
        header = ET.SubElement(root, f"{{{self.namespace_map['cwr']}}}MessageHeader")
        
        message_id = ET.SubElement(header, f"{{{self.namespace_map['cwr']}}}MessageId")
        message_id.text = work_registration.registration_id
        
        message_created = ET.SubElement(header, f"{{{self.namespace_map['cwr']}}}MessageCreatedDateTime")
        message_created.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        sender_name = ET.SubElement(header, f"{{{self.namespace_map['cwr']}}}MessageSender")
        sender_name.text = work_registration.submitter.party_name
        
        # Work registration
        work_registration_elem = ET.SubElement(root, f"{{{self.namespace_map['cwr']}}}WorkRegistration")
        
        # Work
        work = work_registration.work
        work_elem = ET.SubElement(work_registration_elem, f"{{{self.namespace_map['cwr']}}}MusicalWork")
        
        # Work ID
        work_id = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}WorkId")
        if work.iswc:
            iswc = ET.SubElement(work_id, f"{{{self.namespace_map['cwr']}}}ISWC")
            iswc.text = work.iswc
        else:
            # Generate temporary work identifier
            work_number = ET.SubElement(work_id, f"{{{self.namespace_map['cwr']}}}WorkNumber")
            work_number.text = work.work_id
            
        # Work title
        work_title = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}WorkTitle")
        title_text = ET.SubElement(work_title, f"{{{self.namespace_map['cwr']}}}TitleText")
        title_text.text = work.title
        
        if work.sub_title:
            sub_title = ET.SubElement(work_title, f"{{{self.namespace_map['cwr']}}}SubTitle")
            sub_title.text = work.sub_title
        
        # Duration
        if work.duration:
            duration = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}Duration")
            duration.text = work.duration
        
        # Composers
        for composer in work.composers:
            contributor = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}Contributor")
            contributor_name = ET.SubElement(contributor, f"{{{self.namespace_map['cwr']}}}ContributorName")
            contributor_name.text = composer.party_name
            
            contributor_role = ET.SubElement(contributor, f"{{{self.namespace_map['cwr']}}}ContributorRole")
            contributor_role.text = "Composer"
            
            if composer.ipi:
                ipi_elem = ET.SubElement(contributor, f"{{{self.namespace_map['cwr']}}}IPI")
                ipi_elem.text = composer.ipi
        
        # Lyricists  
        for lyricist in work.lyricists:
            contributor = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}Contributor")
            contributor_name = ET.SubElement(contributor, f"{{{self.namespace_map['cwr']}}}ContributorName")
            contributor_name.text = lyricist.party_name
            
            contributor_role = ET.SubElement(contributor, f"{{{self.namespace_map['cwr']}}}ContributorRole")
            contributor_role.text = "Lyricist"
            
            if lyricist.ipi:
                ipi_elem = ET.SubElement(contributor, f"{{{self.namespace_map['cwr']}}}IPI")
                ipi_elem.text = lyricist.ipi
        
        # Publishers
        for publisher in work.publishers:
            publisher_elem = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}Publisher")
            publisher_name = ET.SubElement(publisher_elem, f"{{{self.namespace_map['cwr']}}}PublisherName")
            publisher_name.text = publisher.party_name
            
            if publisher.ipi:
                ipi_elem = ET.SubElement(publisher_elem, f"{{{self.namespace_map['cwr']}}}IPI")
                ipi_elem.text = publisher.ipi
        
        # Rights information
        if work.performing_rights_society:
            rights_society = ET.SubElement(work_elem, f"{{{self.namespace_map['cwr']}}}PerformingRightsSociety")
            rights_society.text = work.performing_rights_society
        
        # Registration details
        registration_territory = ET.SubElement(work_registration_elem, f"{{{self.namespace_map['cwr']}}}RegistrationTerritory")
        registration_territory.text = work_registration.registration_territory.value
        
        registration_date = ET.SubElement(work_registration_elem, f"{{{self.namespace_map['cwr']}}}RegistrationDate")
        registration_date.text = work_registration.registration_date.strftime("%Y-%m-%d")
        
        return self._prettify_xml(root)
    
    def generate_dsr_xml(self, sales_report: DDEXSalesReport) -> str:
        """Generate Digital Sales Report XML"""
        root = ET.Element(
            f"{{{self.namespace_map['dsr']}}}SalesReportMessage",
            attrib={
                "MessageSchemaVersionId": "41",
                "BusinessProfileVersionId": "CommonDealTypes",
                "LanguageAndScriptCode": "en"
            }
        )
        
        # Add namespace
        root.set("xmlns", self.namespace_map['dsr'])
        
        # Message Header
        header = ET.SubElement(root, f"{{{self.namespace_map['dsr']}}}MessageHeader")
        
        message_thread_id = ET.SubElement(header, f"{{{self.namespace_map['dsr']}}}MessageThreadId")
        message_thread_id.text = sales_report.report_id
        
        message_id = ET.SubElement(header, f"{{{self.namespace_map['dsr']}}}MessageId")
        message_id.text = sales_report.report_id
        
        message_created = ET.SubElement(header, f"{{{self.namespace_map['dsr']}}}MessageCreatedDateTime")
        message_created.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Message sender/recipient
        sender = ET.SubElement(header, f"{{{self.namespace_map['dsr']}}}MessageSender")
        sender_party_id = ET.SubElement(sender, f"{{{self.namespace_map['dsr']}}}PartyId")
        sender_party_id.text = sales_report.message_sender.party_id
        sender_party_name = ET.SubElement(sender, f"{{{self.namespace_map['dsr']}}}PartyName")
        sender_party_name.text = sales_report.message_sender.party_name
        
        recipient = ET.SubElement(header, f"{{{self.namespace_map['dsr']}}}MessageRecipient")
        recipient_party_id = ET.SubElement(recipient, f"{{{self.namespace_map['dsr']}}}PartyId")
        recipient_party_id.text = sales_report.message_recipient.party_id
        recipient_party_name = ET.SubElement(recipient, f"{{{self.namespace_map['dsr']}}}PartyName")
        recipient_party_name.text = sales_report.message_recipient.party_name
        
        # Reporting period
        reporting_period = ET.SubElement(root, f"{{{self.namespace_map['dsr']}}}ReportingPeriod")
        start_date = ET.SubElement(reporting_period, f"{{{self.namespace_map['dsr']}}}StartDate")
        start_date.text = sales_report.reporting_period_start.strftime("%Y-%m-%d")
        end_date = ET.SubElement(reporting_period, f"{{{self.namespace_map['dsr']}}}EndDate")
        end_date.text = sales_report.reporting_period_end.strftime("%Y-%m-%d")
        
        # Sales/usage data
        for transaction in sales_report.sales_transactions:
            sales_transaction = ET.SubElement(root, f"{{{self.namespace_map['dsr']}}}SalesTransaction")
            
            # Add transaction details based on the structure
            # This would be expanded based on specific transaction data structure
            transaction_id = ET.SubElement(sales_transaction, f"{{{self.namespace_map['dsr']}}}TransactionId")
            transaction_id.text = transaction.get('transaction_id', '')
        
        return self._prettify_xml(root)
    
    def _prettify_xml(self, root: ET.Element) -> str:
        """Return a pretty-printed XML string"""
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    def validate_xml(self, xml_content: str, schema_type: str) -> bool:
        """Validate XML against DDEX schema (placeholder - would need actual schema files)"""
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError:
            return False
    
    def create_isrc(self, country_code: str = "US", registrant_code: str = "BME", year: str = None) -> str:
        """Generate ISRC (International Standard Recording Code)"""
        if not year:
            year = str(datetime.now().year)[2:]  # Last 2 digits of current year
        
        # Generate unique 5-digit designation code
        designation = f"{uuid.uuid4().hex[:5].upper()}"
        
        return f"{country_code}-{registrant_code}-{year}-{designation}"
    
    def create_iswc(self, work_id: str = None) -> str:
        """Generate ISWC (International Standard Musical Work Code)"""
        if not work_id:
            work_id = uuid.uuid4().hex[:9].upper()
        
        # ISWC format: T-DDD.DDD.DDD-C (where T=prefix, D=digits, C=check digit)
        base_number = f"{work_id[:3]}.{work_id[3:6]}.{work_id[6:9]}"
        
        # Simple check digit calculation (real ISWC uses more complex algorithm)
        check_digit = str(sum(ord(c) for c in work_id.replace('.', '')) % 10)
        
        return f"T-{base_number}-{check_digit}"