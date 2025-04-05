# Face Recognition System API Reference

## Base URL
`http://localhost:8000/api` (Development)  
`https://your-domain.com/api` (Production)

## Authentication
JWT Token (Required for protected endpoints)  
Header: `Authorization: Bearer <token>`

## Endpoints

### 1. System Control

#### Start Processing
```http
POST /start
```
**Request Body**: None  
**Response**:
```json
{
  "status": "started",
  "timestamp": "2023-11-15T14:30:00Z"
}
```

#### Stop Processing
```http
POST /stop
```
**Request Body**: None  
**Response**:
```json
{
  "status": "stopped",
  "timestamp": "2023-11-15T14:35:00Z"
}
```

#### System Status
```http
GET /status
```
**Response**:
```json
{
  "status": "running",
  "detections": [
    {
      "id": "track_1",
      "name": "John Doe",
      "confidence": 0.92,
      "location": [x, y, w, h]
    }
  ],
  "performance": {
    "fps": 28.5,
    "processing_time": 35.2
  }
}
```

### 2. Video Streaming

#### Live Video Feed
```http
GET /video_feed
```
**Response**: MJPEG video stream

### 3. Criminal Database

#### Add Criminal Record
```http
POST /criminals
```
**Request Body**:
```json
{
  "name": "John Doe",
  "image": "base64_encoded_image",
  "metadata": {
    "offenses": ["theft", "burglary"],
    "notes": "Armed and dangerous"
  }
}
```
**Response**:
```json
{
  "id": 42,
  "status": "created",
  "embedding_size": 512
}
```

#### Search Matches
```http
POST /search
```
**Request Body**:
```json
{
  "image": "base64_encoded_image",
  "threshold": 0.85
}
```
**Response**:
```json
{
  "matches": [
    {
      "id": 42,
      "name": "John Doe",
      "confidence": 0.92,
      "metadata": {...}
    }
  ]
}
```

### 4. Alert Management

#### List Recent Alerts
```http
GET /alerts
```
**Query Parameters**:
- `limit`: Number of alerts to return (default: 10)
- `since`: ISO timestamp for filtering

**Response**:
```json
{
  "alerts": [
    {
      "id": "alert_1",
      "name": "John Doe",
      "confidence": 0.92,
      "timestamp": "2023-11-15T14:30:00Z",
      "image": "base64_encoded_image"
    }
  ]
}
```

## WebSocket Events
Endpoint: `ws://localhost:8000`

### Subscriptions
1. **Detections**:
   ```json
   {
     "event": "subscribe",
     "channel": "detections"
   }
   ```
   Payload:
   ```json
   {
     "type": "detection",
     "data": {...}
   }
   ```

2. **Alerts**:
   ```json
   {
     "event": "subscribe",
     "channel": "alerts"
   }
   ```

## Error Responses
```json
{
  "error": {
    "code": 401,
    "message": "Unauthorized",
    "details": "Invalid JWT token"
  }
}
```

## Rate Limits
- 60 requests/minute per endpoint
- 10 concurrent WebSocket connections