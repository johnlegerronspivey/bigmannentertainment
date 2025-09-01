"""
Batch Processing Service for Metadata Parser & Validator
Handles batch operations, bulk uploads, and parallel processing
"""

import asyncio
import zipfile
import tarfile
import gzip
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os

from metadata_models import (
    MetadataFormat, MetadataValidationResult, ParsedMetadata,
    ValidationStatus, MetadataValidationConfig
)
from metadata_parser_service import MetadataParserService
from metadata_validator_service import MetadataValidatorService

logger = logging.getLogger(__name__)

class BatchProcessingResult:
    def __init__(self):
        self.batch_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.end_time = None
        self.total_files = 0
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.file_results = []
        self.status = 'pending'  # pending, processing, completed, failed
        self.errors = []

    def to_dict(self):
        processing_time = None
        if self.end_time and self.start_time:
            processing_time = (self.end_time - self.start_time).total_seconds()
            
        return {
            'batch_id': self.batch_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'status': self.status,
            'success_rate': (self.successful_files / self.total_files * 100) if self.total_files > 0 else 0,
            'file_results': self.file_results,
            'errors': self.errors,
            'processing_time': processing_time
        }

class BatchProcessingService:
    """Service for handling batch metadata operations"""
    
    def __init__(self, mongo_db=None, max_workers=4):
        self.mongo_db = mongo_db
        self.max_workers = max_workers
        self.parser_service = MetadataParserService()
        self.validator_service = MetadataValidatorService(mongo_db=mongo_db)
        self.active_batches = {}  # Store active batch processing status
        
    async def process_archive(self, archive_content: bytes, filename: str, user_id: str, 
                            validation_config: Optional[MetadataValidationConfig] = None) -> BatchProcessingResult:
        """Process uploaded archive file (ZIP, TAR, GZ)"""
        
        batch_result = BatchProcessingResult()
        batch_result.status = 'processing'
        self.active_batches[batch_result.batch_id] = batch_result
        
        try:
            # Extract files from archive
            extracted_files = await self._extract_archive(archive_content, filename)
            batch_result.total_files = len(extracted_files)
            
            if extracted_files:
                # Process files in parallel
                await self._process_files_parallel(
                    extracted_files, 
                    batch_result, 
                    user_id, 
                    validation_config
                )
            
            batch_result.status = 'completed'
            batch_result.end_time = datetime.now()
            
            # Store batch result in database
            await self._store_batch_result(batch_result, user_id)
            
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            batch_result.status = 'failed'
            batch_result.end_time = datetime.now()
            batch_result.errors.append(f"Batch processing failed: {str(e)}")
            
        finally:
            # Keep batch result for a short time for status queries
            asyncio.create_task(self._cleanup_batch(batch_result.batch_id))
            
        return batch_result
    
    async def process_multiple_files(self, files_data: List[Dict], user_id: str,
                                   validation_config: Optional[MetadataValidationConfig] = None) -> BatchProcessingResult:
        """Process multiple individual files"""
        
        batch_result = BatchProcessingResult()
        batch_result.status = 'processing'
        batch_result.total_files = len(files_data)
        self.active_batches[batch_result.batch_id] = batch_result
        
        try:
            # Convert files_data to format expected by _process_files_parallel
            extracted_files = []
            for file_data in files_data:
                extracted_files.append({
                    'filename': file_data.get('filename', 'unknown'),
                    'content': file_data.get('content', b''),
                    'format': file_data.get('format', MetadataFormat.JSON)
                })
            
            # Process files in parallel
            await self._process_files_parallel(
                extracted_files, 
                batch_result, 
                user_id, 
                validation_config
            )
            
            batch_result.status = 'completed'
            batch_result.end_time = datetime.now()
            
            # Store batch result in database
            await self._store_batch_result(batch_result, user_id)
            
        except Exception as e:
            logger.error(f"Multi-file processing error: {str(e)}")
            batch_result.status = 'failed'
            batch_result.end_time = datetime.now()
            batch_result.errors.append(f"Multi-file processing failed: {str(e)}")
            
        return batch_result
    
    async def _extract_archive(self, content: bytes, filename: str) -> List[Dict]:
        """Extract files from archive"""
        
        extracted_files = []
        
        try:
            if filename.lower().endswith('.zip'):
                extracted_files = await self._extract_zip(content)
            elif filename.lower().endswith(('.tar', '.tar.gz', '.tgz')):
                extracted_files = await self._extract_tar(content)
            elif filename.lower().endswith('.gz'):
                extracted_files = await self._extract_gzip(content, filename)
            else:
                raise ValueError(f"Unsupported archive format: {filename}")
                
        except Exception as e:
            logger.error(f"Archive extraction error: {str(e)}")
            raise
            
        return extracted_files
    
    async def _extract_zip(self, content: bytes) -> List[Dict]:
        """Extract ZIP archive"""
        
        extracted_files = []
        
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_file:
            for file_info in zip_file.filelist:
                if not file_info.is_dir() and self._is_metadata_file(file_info.filename):
                    try:
                        file_content = zip_file.read(file_info.filename)
                        extracted_files.append({
                            'filename': file_info.filename,
                            'content': file_content,
                            'format': self._detect_format_from_filename(file_info.filename)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to extract {file_info.filename}: {str(e)}")
                        
        return extracted_files
    
    async def _extract_tar(self, content: bytes) -> List[Dict]:
        """Extract TAR archive"""
        
        extracted_files = []
        
        with tarfile.open(fileobj=io.BytesIO(content), mode='r:*') as tar_file:
            for member in tar_file.getmembers():
                if member.isfile() and self._is_metadata_file(member.name):
                    try:
                        file_obj = tar_file.extractfile(member)
                        if file_obj:
                            file_content = file_obj.read()
                            extracted_files.append({
                                'filename': member.name,
                                'content': file_content,
                                'format': self._detect_format_from_filename(member.name)
                            })
                    except Exception as e:
                        logger.warning(f"Failed to extract {member.name}: {str(e)}")
                        
        return extracted_files
    
    async def _extract_gzip(self, content: bytes, filename: str) -> List[Dict]:
        """Extract GZIP file"""
        
        try:
            with gzip.open(io.BytesIO(content), 'rb') as gz_file:
                decompressed_content = gz_file.read()
                
                # Remove .gz extension to get original filename
                original_filename = filename[:-3] if filename.endswith('.gz') else filename
                
                if self._is_metadata_file(original_filename):
                    return [{
                        'filename': original_filename,
                        'content': decompressed_content,
                        'format': self._detect_format_from_filename(original_filename)
                    }]
                    
        except Exception as e:
            logger.error(f"GZIP extraction error: {str(e)}")
            
        return []
    
    def _is_metadata_file(self, filename: str) -> bool:
        """Check if file is a metadata file"""
        
        metadata_extensions = [
            '.json', '.xml', '.csv', '.txt', '.ddex', '.mead', 
            '.id3', '.musicbrainz', '.yml', '.yaml'
        ]
        
        return any(filename.lower().endswith(ext) for ext in metadata_extensions)
    
    def _detect_format_from_filename(self, filename: str) -> MetadataFormat:
        """Detect metadata format from filename"""
        
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.json') or 'json' in filename_lower:
            return MetadataFormat.JSON
        elif filename_lower.endswith('.xml') or filename_lower.endswith('.ddex'):
            if 'ddex' in filename_lower or 'ern' in filename_lower:
                return MetadataFormat.DDEX_ERN
            else:
                return MetadataFormat.MEAD
        elif filename_lower.endswith('.csv'):
            return MetadataFormat.CSV
        elif 'mead' in filename_lower:
            return MetadataFormat.MEAD
        else:
            return MetadataFormat.JSON  # Default
    
    async def _process_files_parallel(self, files: List[Dict], batch_result: BatchProcessingResult,
                                    user_id: str, validation_config: Optional[MetadataValidationConfig]):
        """Process multiple files in parallel"""
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_single_file(file_data: Dict):
            async with semaphore:
                return await self._process_single_file_in_batch(
                    file_data, 
                    batch_result, 
                    user_id, 
                    validation_config
                )
        
        # Create tasks for all files
        tasks = [process_single_file(file_data) for file_data in files]
        
        # Process files in parallel
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_file_in_batch(self, file_data: Dict, batch_result: BatchProcessingResult,
                                          user_id: str, validation_config: Optional[MetadataValidationConfig]):
        """Process a single file within a batch"""
        
        filename = file_data['filename']
        
        try:
            # Parse metadata
            parsed_metadata, parsing_errors = self.parser_service.parse_metadata(
                content=file_data['content'],
                file_format=file_data['format'],
                file_name=filename
            )
            
            # Validate if config provided
            validation_result = None
            if validation_config:
                validation_result = await self.validator_service.validate_metadata(
                    parsed_metadata=parsed_metadata,
                    file_format=file_data['format'],
                    config=validation_config
                )
                validation_result.user_id = user_id
                validation_result.file_name = filename
                validation_result.file_size = len(file_data['content'])
                validation_result.parsing_errors = parsing_errors
            
            # Create result entry
            file_result = {
                'filename': filename,
                'status': 'success',
                'format': file_data['format'].value,
                'parsed_metadata': parsed_metadata.dict() if parsed_metadata else None,
                'validation_result': validation_result.dict() if validation_result else None,
                'parsing_errors': [error.dict() for error in parsing_errors],
                'file_size': len(file_data['content'])
            }
            
            batch_result.file_results.append(file_result)
            batch_result.successful_files += 1
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            
            file_result = {
                'filename': filename,
                'status': 'error',
                'error': str(e),
                'file_size': len(file_data['content'])
            }
            
            batch_result.file_results.append(file_result)
            batch_result.failed_files += 1
            
        finally:
            batch_result.processed_files += 1
    
    async def _store_batch_result(self, batch_result: BatchProcessingResult, user_id: str):
        """Store batch processing result in database"""
        
        if self.mongo_db is None:
            return
            
        try:
            result_dict = batch_result.to_dict()
            result_dict['user_id'] = user_id
            result_dict['_id'] = batch_result.batch_id
            result_dict['created_at'] = datetime.now()
            
            await self.mongo_db["batch_processing_results"].insert_one(result_dict)
            logger.info(f"Stored batch result {batch_result.batch_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store batch result: {str(e)}")
    
    async def _cleanup_batch(self, batch_id: str, delay_seconds: int = 300):
        """Clean up batch result from memory after delay"""
        
        await asyncio.sleep(delay_seconds)
        
        if batch_id in self.active_batches:
            del self.active_batches[batch_id]
            logger.info(f"Cleaned up batch {batch_id}")
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Get current status of a batch processing job"""
        
        if batch_id in self.active_batches:
            return self.active_batches[batch_id].to_dict()
        
        return None
    
    async def get_batch_history(self, user_id: str, limit: int = 20, offset: int = 0) -> Dict:
        """Get batch processing history for user"""
        
        if self.mongo_db is None:
            return {'batches': [], 'total_count': 0}
            
        try:
            query = {'user_id': user_id}
            
            # Get total count
            total_count = await self.mongo_db["batch_processing_results"].count_documents(query)
            
            # Get paginated results
            cursor = self.mongo_db["batch_processing_results"].find(query).sort("created_at", -1).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id for response
            for result in results:
                result.pop("_id", None)
            
            return {
                'batches': results,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error getting batch history: {str(e)}")
            return {'batches': [], 'total_count': 0}
    
    async def generate_batch_report(self, batch_id: str, user_id: str) -> Optional[Dict]:
        """Generate detailed report for a batch processing job"""
        
        if self.mongo_db is None:
            return None
            
        try:
            batch_result = await self.mongo_db["batch_processing_results"].find_one({
                "_id": batch_id,
                "user_id": user_id
            })
            
            if not batch_result:
                return None
            
            # Calculate additional statistics
            report = {
                'batch_info': {
                    'batch_id': batch_id,
                    'total_files': batch_result.get('total_files', 0),
                    'successful_files': batch_result.get('successful_files', 0),
                    'failed_files': batch_result.get('failed_files', 0),
                    'success_rate': batch_result.get('success_rate', 0),
                    'processing_time': batch_result.get('processing_time', 0),
                    'start_time': batch_result.get('start_time'),
                    'end_time': batch_result.get('end_time'),
                    'status': batch_result.get('status')
                },
                'file_statistics': {
                    'formats_processed': {},
                    'validation_summary': {
                        'valid': 0,
                        'warning': 0,
                        'error': 0
                    },
                    'duplicates_found': 0,
                    'total_file_size': 0
                },
                'detailed_results': batch_result.get('file_results', [])
            }
            
            # Calculate statistics from file results
            for file_result in batch_result.get('file_results', []):
                # Format statistics
                file_format = file_result.get('format', 'unknown')
                report['file_statistics']['formats_processed'][file_format] = \
                    report['file_statistics']['formats_processed'].get(file_format, 0) + 1
                
                # Validation statistics
                validation_result = file_result.get('validation_result')
                if validation_result:
                    status = validation_result.get('validation_status', 'unknown')
                    if status in report['file_statistics']['validation_summary']:
                        report['file_statistics']['validation_summary'][status] += 1
                    
                    # Duplicates
                    duplicate_count = validation_result.get('duplicate_count', 0)
                    report['file_statistics']['duplicates_found'] += duplicate_count
                
                # File size
                file_size = file_result.get('file_size', 0)
                report['file_statistics']['total_file_size'] += file_size
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating batch report: {str(e)}")
            return None