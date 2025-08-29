# Supabase Production Database Setup

## 1. Create Supabase Project
1. Go to https://supabase.com
2. Create new project
3. Choose region (recommend US East for Render compatibility)
4. Set strong database password

## 2. Get Connection String
1. Go to Project Settings → Database
2. Copy connection string from "Connection pooling" section
3. Format: `postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require`

## 3. Update Render Environment
1. Go to Render dashboard → Your service
2. Environment tab
3. Update DATABASE_URL with your Supabase connection string
4. Redeploy service

## 4. Verify Connection
```bash
# Test health endpoint
curl https://prompt-to-json-agent-backend-1.onrender.com/health

# Create a test report
curl -X POST https://prompt-to-json-agent-backend-1.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test supabase connection"}'
```

## 5. Database Tables
Tables will be auto-created on first connection:
- `reports` - JSON specifications
- `evaluations` - Scoring results  
- `iterations` - RL improvement history
- `feedback_logs` - Generated feedback
- `hidg_values` - Daily reflection logs

## Production Benefits
- **Scalability**: Handles 50+ concurrent users
- **Reliability**: Managed Postgres with backups
- **Performance**: Connection pooling enabled
- **BHIV Bucket**: Structured data storage as required