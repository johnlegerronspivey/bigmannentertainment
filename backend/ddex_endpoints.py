from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import os
from pathlib import Path

from .server import get_current_user, get_current_admin_user, db, User, log_activity
from .ddex_models import *
from .ddex_service import DDEXService

# Create DDEX router
ddex_router = APIRouter(prefix="/api/ddex", tags=["DDEX"])

# Initialize DDEX service
ddex_service = DDEXService()

# DDEX storage directory
ddex_dir = Path("/app/ddex_messages")
ddex_dir.mkdir(exist_ok=True)

@ddex_router.post("/ern/create", response_model=Dict[str, Any])
async def create_ern_message(
    title: str = Form(...),
    artist_name: str = Form(...),
    label_name: str = Form(...),
    release_date: str = Form(...),
    release_type: str = Form("Single"),
    territories: str = Form("Worldwide"),
    audio_file: UploadFile = File(...),
    cover_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Create Electronic Release Notification (ERN) message for digital distribution"""
    
    try:
        # Parse release date
        parsed_release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
        
        # Save uploaded files
        audio_path = ddex_dir / f"audio_{uuid.uuid4().hex[:8]}_{audio_file.filename}"
        async with open(audio_path, "wb") as f:
            content = await audio_file.read()
            await f.write(content)
        
        cover_path = None
        if cover_image:
            cover_path = ddex_dir / f"cover_{uuid.uuid4().hex[:8]}_{cover_image.filename}"
            async with open(cover_path, "wb") as f:
                content = await cover_image.read()
                await f.write(content)
        
        # Create DDEX Party for artist
        artist_party = DDEXParty(
            party_name=artist_name,
            party_type="Artist",
            dpid=f"ARTIST_{uuid.uuid4().hex[:8].upper()}"
        )
        
        # Create DDEX Party for label
        label_party = DDEXParty(
            party_name=label_name,
            party_type="Label",
            dpid=f"LABEL_{uuid.uuid4().hex[:8].upper()}"
        )
        
        # Create audio resource
        audio_resource = DDEXResource(
            resource_type="SoundRecording",
            title=title,
            file_path=str(audio_path),
            mime_type=audio_file.content_type,
            file_size=len(content),
            artists=[artist_party],
            isrc=ddex_service.create_isrc(),
            copyright_year=parsed_release_date.year,
            production_year=parsed_release_date.year,
            genre="Pop",  # Default, could be parameterized
            parental_warning_type="NotExplicit"
        )
        
        # Add technical details for audio
        if "audio" in audio_file.content_type.lower():
            audio_resource.bitrate = 320  # Default values
            audio_resource.sample_rate = 44100
            audio_resource.channels = 2
            audio_resource.duration = "PT3M30S"  # Placeholder duration
        
        resources = [audio_resource]
        
        # Create cover image resource if provided
        if cover_image and cover_path:
            cover_resource = DDEXResource(
                resource_type="Image",
                title=f"{title} - Cover Art",
                file_path=str(cover_path),
                mime_type=cover_image.content_type,
                file_size=len(await cover_image.read())
            )
            resources.append(cover_resource)
        
        # Create release
        release = DDEXRelease(
            release_type=ReleaseType(release_type),
            title=title,
            display_artist=artist_name,
            label_name=label_name,
            release_date=parsed_release_date,
            resources=resources,
            territories=[TerritoryCode(territories)],
            rights_granted=[RightsType.ON_DEMAND_STREAM, RightsType.PERMANENT_DOWNLOAD],
            rights_controller=label_party,
            marketing_label=label_party,
            catalog_number=f"BME{parsed_release_date.year}{uuid.uuid4().hex[:6].upper()}"
        )
        
        # Create ERN message
        ern_message = DDEXMessage(
            message_type=DDEXMessageType.ERN,
            release=release,
            recipient_name="Digital Service Provider",
            recipient_id="DSP001"
        )
        
        # Generate XML
        xml_content = ddex_service.generate_ern_xml(ern_message)
        
        # Save XML file
        xml_filename = f"ERN_{ern_message.message_id}.xml"
        xml_path = ddex_dir / xml_filename
        
        async with open(xml_path, "w", encoding="utf-8") as f:
            await f.write(xml_content)
        
        # Store in database
        ddex_record = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "message_type": "ERN",
            "message_id": ern_message.message_id,
            "title": title,
            "artist_name": artist_name,
            "label_name": label_name,
            "release_date": parsed_release_date,
            "xml_filename": xml_filename,
            "xml_path": str(xml_path),
            "audio_path": str(audio_path),
            "cover_path": str(cover_path) if cover_path else None,
            "isrc": audio_resource.isrc,
            "catalog_number": release.catalog_number,
            "status": "Created",
            "created_at": datetime.utcnow(),
            "territories": territories,
            "rights_granted": [right.value for right in release.rights_granted]
        }
        
        await db.ddex_messages.insert_one(ddex_record)
        
        # Log activity
        await log_activity(
            current_user.id,
            "ddex_ern_created",
            "ddex_message",
            ddex_record["id"],
            {
                "title": title,
                "artist": artist_name,
                "message_id": ern_message.message_id,
                "isrc": audio_resource.isrc
            }
        )
        
        return {
            "message": "ERN message created successfully",
            "message_id": ern_message.message_id,
            "xml_filename": xml_filename,
            "isrc": audio_resource.isrc,
            "catalog_number": release.catalog_number,
            "record_id": ddx_record["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ERN message: {str(e)}")

@ddex_router.post("/cwr/register-work", response_model=Dict[str, Any])
async def register_musical_work(
    title: str = Form(...),
    composer_name: str = Form(...),
    lyricist_name: str = Form(None),
    publisher_name: str = Form(None),
    performing_rights_org: str = Form("ASCAP"),
    duration: str = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Register musical work with Performance Rights Organizations via CWR"""
    
    try:
        # Create composer party
        composer = DDEXParty(
            party_name=composer_name,
            party_type="Composer",
            ipi=f"00000000{uuid.uuid4().hex[:3].upper()}"  # Placeholder IPI
        )
        
        composers = [composer]
        lyricists = []
        publishers = []
        
        # Add lyricist if provided
        if lyricist_name:
            lyricist = DDEXParty(
                party_name=lyricist_name,
                party_type="Lyricist",
                ipi=f"00000000{uuid.uuid4().hex[:3].upper()}"
            )
            lyricists.append(lyricist)
        
        # Add publisher if provided
        if publisher_name:
            publisher = DDEXParty(
                party_name=publisher_name,
                party_type="Publisher",
                ipi=f"00000000{uuid.uuid4().hex[:3].upper()}"
            )
            publishers.append(publisher)
        
        # Create musical work
        musical_work = DDEXMusicalWork(
            title=title,
            composers=composers,
            lyricists=lyricists,
            publishers=publishers,
            performing_rights_society=performing_rights_org,
            duration=duration,
            copyright_year=datetime.now().year,
            iswc=ddex_service.create_iswc()
        )
        
        # Create submitter (current user/company)
        submitter = DDEXParty(
            party_name=current_user.full_name or current_user.business_name or "Big Mann Entertainment",
            party_type="Submitter",
            email=current_user.email,
            dpid=f"SUB_{current_user.id[:8].upper()}"
        )
        
        # Create work registration
        work_registration = DDEXWorkRegistration(
            work=musical_work,
            performing_rights_organization=performing_rights_org,
            submitter=submitter,
            contact_info={
                "email": current_user.email,
                "name": current_user.full_name
            }
        )
        
        # Generate CWR XML
        xml_content = ddex_service.generate_cwr_xml(work_registration)
        
        # Save XML file
        xml_filename = f"CWR_{work_registration.registration_id}.xml"
        xml_path = ddex_dir / xml_filename
        
        async with open(xml_path, "w", encoding="utf-8") as f:
            await f.write(xml_content)
        
        # Store in database
        cwr_record = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "message_type": "CWR",
            "registration_id": work_registration.registration_id,
            "title": title,
            "composer_name": composer_name,
            "lyricist_name": lyricist_name,
            "publisher_name": publisher_name,
            "performing_rights_org": performing_rights_org,
            "xml_filename": xml_filename,
            "xml_path": str(xml_path),
            "iswc": musical_work.iswc,
            "work_id": musical_work.work_id,
            "status": "Registered",
            "created_at": datetime.utcnow(),
            "registration_date": work_registration.registration_date
        }
        
        await db.ddex_cwr_registrations.insert_one(cwr_record)
        
        # Log activity
        await log_activity(
            current_user.id,
            "ddex_cwr_registered",
            "musical_work",
            cwr_record["id"],
            {
                "title": title,
                "composer": composer_name,
                "iswc": musical_work.iswc,
                "performing_rights_org": performing_rights_org
            }
        )
        
        return {
            "message": "Musical work registered successfully",
            "registration_id": work_registration.registration_id,
            "xml_filename": xml_filename,
            "iswc": musical_work.iswc,
            "work_id": musical_work.work_id,
            "record_id": cwr_record["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register musical work: {str(e)}")

@ddex_router.get("/messages")
async def get_ddex_messages(
    message_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get user's DDEX messages"""
    
    query = {"user_id": current_user.id}
    if message_type:
        query["message_type"] = message_type.upper()
    
    # Get ERN messages
    ern_messages = await db.ddex_messages.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Get CWR registrations
    cwr_messages = await db.ddex_cwr_registrations.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Combine and sort
    all_messages = ern_messages + cwr_messages
    all_messages.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "messages": all_messages[:limit],
        "total": len(all_messages)
    }

@ddex_router.get("/messages/{message_id}")
async def get_ddex_message_details(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific DDEX message details"""
    
    # Try ERN messages first
    message = await db.ddex_messages.find_one({
        "id": message_id,
        "user_id": current_user.id
    })
    
    if not message:
        # Try CWR registrations
        message = await db.ddex_cwr_registrations.find_one({
            "id": message_id,
            "user_id": current_user.id
        })
    
    if not message:
        raise HTTPException(status_code=404, detail="DDEX message not found")
    
    return message

@ddx_router.get("/messages/{message_id}/xml")
async def download_ddx_xml(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download DDEX XML file"""
    
    # Get message details
    message = await get_ddex_message_details(message_id, current_user)
    
    xml_path = Path(message["xml_path"])
    if not xml_path.exists():
        raise HTTPException(status_code=404, detail="XML file not found")
    
    # Return file response
    from fastapi.responses import FileResponse
    return FileResponse(
        path=xml_path,
        filename=message["xml_filename"],
        media_type="application/xml"
    )

@ddex_router.post("/validate")
async def validate_ddex_xml(
    xml_file: UploadFile = File(...),
    schema_type: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Validate DDEX XML against schema"""
    
    try:
        content = await xml_file.read()
        xml_content = content.decode('utf-8')
        
        is_valid = ddex_service.validate_xml(xml_content, schema_type)
        
        return {
            "valid": is_valid,
            "schema_type": schema_type,
            "filename": xml_file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

@ddex_router.get("/identifiers/generate")
async def generate_identifiers(
    identifier_type: str,  # isrc, iswc, catalog_number
    count: int = 1,
    current_user: User = Depends(get_current_user)
):
    """Generate music industry standard identifiers"""
    
    if identifier_type.lower() not in ["isrc", "iswc", "catalog_number"]:
        raise HTTPException(status_code=400, detail="Invalid identifier type")
    
    identifiers = []
    
    for _ in range(min(count, 10)):  # Limit to 10 at a time
        if identifier_type.lower() == "isrc":
            identifier = ddx_service.create_isrc()
        elif identifier_type.lower() == "iswc":
            identifier = ddex_service.create_iswc()
        elif identifier_type.lower() == "catalog_number":
            year = datetime.now().year
            identifier = f"BME{year}{uuid.uuid4().hex[:6].upper()}"
        
        identifiers.append(identifier)
    
    # Log activity
    await log_activity(
        current_user.id,
        "ddex_identifiers_generated",
        "identifier",
        None,
        {
            "type": identifier_type,
            "count": len(identifiers),
            "identifiers": identifiers
        }
    )
    
    return {
        "identifier_type": identifier_type,
        "identifiers": identifiers,
        "count": len(identifiers)
    }

@ddex_router.get("/admin/messages", dependencies=[Depends(get_current_admin_user)])
async def get_all_ddx_messages(
    message_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Admin: Get all DDEX messages across all users"""
    
    query = {}
    if message_type:
        query["message_type"] = message_type.upper()
    if status:
        query["status"] = status
    
    # Get ERN messages
    ern_messages = await db.ddex_messages.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Get CWR registrations  
    cwr_messages = await db.ddex_cwr_registrations.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Add user information
    all_messages = ern_messages + cwr_messages
    for message in all_messages:
        user = await db.users.find_one({"id": message["user_id"]}, {"full_name": 1, "email": 1})
        message["user"] = user
    
    all_messages.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "messages": all_messages[:limit],
        "total": len(all_messages)
    }

@ddx_router.get("/admin/statistics", dependencies=[Depends(get_current_admin_user)])
async def get_ddex_statistics():
    """Admin: Get DDEX usage statistics"""
    
    # Count messages by type
    ern_count = await db.ddex_messages.count_documents({})
    cwr_count = await db.ddex_cwr_registrations.count_documents({})
    
    # Count by status
    pending_ern = await db.ddex_messages.count_documents({"status": "Created"})
    pending_cwr = await db.ddex_cwr_registrations.count_documents({"status": "Registered"})
    
    # Recent activity (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_ern = await db.ddex_messages.count_documents({"created_at": {"$gte": thirty_days_ago}})
    recent_cwr = await db.ddex_cwr_registrations.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    return {
        "total_messages": ern_count + cwr_count,
        "ern_messages": ern_count,
        "cwr_registrations": cwr_count,
        "pending_processing": pending_ern + pending_cwr,
        "recent_activity": {
            "ern_messages_30_days": recent_ern,
            "cwr_registrations_30_days": recent_cwr,
            "total_30_days": recent_ern + recent_cwr
        }
    }