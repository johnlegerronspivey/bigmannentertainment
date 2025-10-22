# DPID Integration Documentation

## Overview
Digital Provider ID (DPID) has been successfully integrated into the Big Mann Entertainment platform for music industry identification and DDEX messaging.

## DPID Details
- **DPID Value**: `PADPIDA2018072700C`
- **Entity**: Big Mann Entertainment
- **Owner**: John LeGerron Spivey
- **Purpose**: Digital service provider identification for music distribution and rights management

## Integration Locations

### 1. Environment Variables (`/app/backend/.env`)
```bash
DPID="PADPIDA2018072700C"
```
Added to Product and Global Identification Numbers section alongside:
- UPC_COMPANY_PREFIX
- GLOBAL_LOCATION_NUMBER
- ISRC_PREFIX
- PUBLISHER_NUMBER
- IPI_NUMBER_COMPANY
- IPI_NUMBER_INDIVIDUAL
- IPN_NUMBER
- ISNI_NUMBER_INDIVIDUAL
- AARC_NUMBER_COMPANY
- AARC_NUMBER_INDIVIDUAL

### 2. Business Information Service (`business_information_service.py`)

#### Model Definition
```python
class BusinessInformation(BaseModel):
    # ... other fields ...
    
    # DPID Identifier
    dpid: Optional[str] = None  # Digital Provider ID for music industry
```

#### Default Business Information
```python
self.default_business_info = {
    "business_entity": "Big Mann Entertainment",
    "business_owner": "John LeGerron Spivey",
    # ... other fields ...
    "dpid": "PADPIDA2018072700C",
    # ... other fields ...
}
```

#### Database Index
```python
await self.business_info_collection.create_indexes([
    IndexModel([("business_id", 1)], unique=True),
    IndexModel([("ein", 1)]),
    IndexModel([("tin", 1)]),
    IndexModel([("legal_entity_gln", 1)]),
    IndexModel([("company_prefix", 1)]),
    IndexModel([("dpid", 1)])  # DPID indexed for efficient lookups
])
```

### 3. DDEX Integration (`ddex_endpoints.py`)

#### Automatic DPID Assignment
When creating DDEX messages, the system automatically uses the correct DPID for Big Mann Entertainment:

```python
# Create DDEX Party for label
# Use actual DPID for Big Mann Entertainment
label_dpid = "PADPIDA2018072700C" if label_name == "Big Mann Entertainment" else f"LABEL_{uuid.uuid4().hex[:8].upper()}"
label_party = DDEXParty(
    party_name=label_name,
    party_type="Label",
    dpid=label_dpid
)
```

### 4. DDEX Models (`ddex_models.py`)

#### DDEXParty Model
```python
class DDEXParty(BaseModel):
    party_id: str = Field(default_factory=lambda: f"PARTY_{uuid.uuid4().hex[:8].upper()}")
    party_name: str
    party_type: str  # Label, Artist, Distributor, Publisher, etc.
    dpid: Optional[str] = None  # DDEX Party Identifier
    isni: Optional[str] = None  # International Standard Name Identifier
    ipi: Optional[str] = None   # Interested Parties Information
    ipn: Optional[str] = None   # IPI Name Number
```

## Usage Examples

### 1. Accessing DPID via Business Information API
```python
GET /api/comprehensive-licensing/business-information
Authorization: Bearer {token}

Response:
{
    "business_information": {
        "business_entity": "Big Mann Entertainment",
        "dpid": "PADPIDA2018072700C",
        // ... other fields ...
    }
}
```

### 2. DDEX Message Generation
When creating ERN (Electronic Release Notification) messages:
- If label is "Big Mann Entertainment", DPID `PADPIDA2018072700C` is automatically used
- If label is different, a temporary DPID is generated

### 3. Database Queries
```python
# Find business information by DPID
business_info = await db.business_information.find_one({"dpid": "PADPIDA2018072700C"})

# Use indexed DPID for efficient lookups
businesses = await db.business_information.find({"dpid": {"$exists": True}})
```

## DPID Standards and Format

### Format Specification
- **Prefix**: `PADPID` - Party ID type identifier
- **Scheme**: `A` - Scheme identifier
- **Date**: `20180727` - Date of registration (July 27, 2018)
- **Sequence**: `00C` - Sequence number

### Industry Usage
The DPID is used for:
1. **DDEX Messaging**: Identifying parties in digital music supply chain
2. **Rights Management**: Tracking ownership and distribution rights
3. **Royalty Distribution**: Ensuring correct payment routing
4. **Platform Integration**: Connecting with music distribution services
5. **Compliance**: Meeting industry standards for digital service providers

## Benefits

1. **Industry Recognition**: Official DPID provides legitimacy in music industry
2. **Automated Integration**: DDEX messages automatically include correct DPID
3. **Rights Tracking**: Enables proper attribution in digital music ecosystem
4. **Standard Compliance**: Meets DDEX and music industry standards
5. **Database Indexing**: Fast lookups and efficient queries

## Related Identifiers

Big Mann Entertainment also uses:
- **GLN (Global Location Number)**: 0860004340201
- **Company Prefix**: 8600043402
- **ISRC Prefix**: QZ9H8
- **IPI Number**: 813048171
- **ISNI Number**: 0000000491551894
- **AARC Number**: RC00002057

## API Endpoints Using DPID

1. **Business Information**:
   - `GET /api/comprehensive-licensing/business-information`
   - `PUT /api/comprehensive-licensing/business-information/{business_id}`

2. **DDEX Messages**:
   - `POST /api/ddex/ern/create` - Electronic Release Notification
   - `POST /api/ddex/cwr/create` - Common Works Registration
   - `POST /api/ddex/messages` - General DDEX message creation

3. **Licensing**:
   - All comprehensive licensing endpoints include business information with DPID

## Maintenance

### Updating DPID
If the DPID needs to be updated:

1. Update `/app/backend/.env`:
   ```bash
   DPID="NEW_DPID_VALUE"
   ```

2. Update `business_information_service.py` default:
   ```python
   "dpid": "NEW_DPID_VALUE"
   ```

3. Update `ddex_endpoints.py` constant:
   ```python
   label_dpid = "NEW_DPID_VALUE" if label_name == "Big Mann Entertainment" ...
   ```

4. Restart backend:
   ```bash
   sudo supervisorctl restart bme_services:backend
   ```

## Verification

To verify DPID integration:

```bash
# Check environment variable
grep DPID /app/backend/.env

# Check business information service
grep -n "PADPIDA2018072700C" /app/backend/business_information_service.py

# Check DDEX endpoints
grep -n "PADPIDA2018072700C" /app/backend/ddex_endpoints.py
```

## Support

For questions about DPID integration:
- Technical documentation: This file
- Business information API: `/api/comprehensive-licensing/business-information`
- DDEX documentation: `/api/ddex/docs`

---

**Last Updated**: January 16, 2025
**Integration Version**: 1.0
**Status**: ✅ Fully Integrated and Operational
