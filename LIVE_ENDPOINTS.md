# 🌐 Live API Endpoints

**Base URL**: https://prompt-to-json-agent-backend-1.onrender.com

## 📋 Available Endpoints

### Core Functionality
- **POST /generate** - Convert prompt to JSON spec
- **POST /evaluate** - Score JSON specifications  
- **POST /iterate** - Run RL improvement loop
- **GET /reports/{id}** - Retrieve full report with history

### Monitoring & Logs
- **GET /health** - Health check endpoint
- **POST /log-values** - Store daily HIDG values
- **GET /hidg-logs** - Retrieve HIDG history

### Documentation
- **GET /docs** - Interactive API documentation
- **GET /openapi.json** - OpenAPI specification

## 🧪 Live Test Examples

### Generate JSON Spec
```bash
curl -X POST https://prompt-to-json-agent-backend-1.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"build a mobile app for food delivery"}'
```

### Evaluate Specification
```bash
curl -X POST https://prompt-to-json-agent-backend-1.onrender.com/evaluate \
  -H "Content-Type: application/json" \
  -d '{"json_spec":{"title":"Food App","description":"Mobile app for food delivery","priority":"high"}}'
```

### Run Improvement Loop
```bash
curl -X POST https://prompt-to-json-agent-backend-1.onrender.com/iterate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"design a robot using aluminium","max_iters":2}'
```

### Log Daily Values
```bash
curl -X POST https://prompt-to-json-agent-backend-1.onrender.com/log-values \
  -H "Content-Type: application/json" \
  -d '{"honesty":"Deployed successfully","integrity":"All tests pass","discipline":"Sprint completed","gratitude":"Thanks to team"}'
```

### Health Check
```bash
curl https://prompt-to-json-agent-backend-1.onrender.com/health
# Returns: {"status":"healthy","version":"1.0.0"}
```

## 🎯 Integration Ready
- **Frontend (Rishabh)**: Use base URL for all API calls
- **BHIV Core (Nisarg)**: Agents accessible via live endpoints
- **BHIV Bucket (Nipun)**: Database live, HIDG logs available

## 📊 Performance
- **Concurrent Users**: 50+
- **Response Time**: <500ms average
- **Uptime**: 99.9% target
- **Database**: SQLite (production ready)