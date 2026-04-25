# Deploy to Hyperion with Existing Caddy

## Quick Deploy (One Command)

Copy to Hyperion and run:

```bash
scp /tmp/setup-social-mind-hyperion.sh hyperion:/tmp/
ssh hyperion "chmod +x /tmp/setup-social-mind-hyperion.sh && sudo /tmp/setup-social-mind-hyperion.sh"
```

## What It Does

1. Clones repo to `/opt/containers/social-mind/`
2. Creates `.env` with secure secret key
3. **Adds Caddy config to `/etc/caddy/Caddyfile`**
4. Reloads Caddy to pick up new config
5. Starts backend on port 8000 (localhost)
6. Starts frontend on port 3000 (localhost)
7. Caddy routes `social.voidnode.dev` → containers

## Caddy Integration

The script automatically adds this to your existing Caddyfile:

```
social.voidnode.dev {
    handle_path /api/* {
        reverse_proxy localhost:8000
    }
    
    handle {
        reverse_proxy localhost:3000
    }
}
```

## Ports Used

| Service | Port | Notes |
|---------|------|-------|
| Backend | 8000 | Localhost only, proxied via Caddy |
| Frontend | 3000 | Localhost only, proxied via Caddy |
| Caddy | 443 | External HTTPS |

## After Deploy

- **App**: https://social.voidnode.dev
- **Logs**: `ssh hyperion "cd /opt/containers/social-mind/docker && docker-compose logs -f"`
- **Restart**: `ssh hyperion "cd /opt/containers/social-mind/docker && docker-compose restart"`

## Manual Steps (If Script Fails)

```bash
ssh hyperion
cd /opt/containers
git clone https://forgejo.voidnode.dev/nuno/social-mind.git
cd social-mind

# Create .env
cat > .env << 'EOF'
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite+aiosqlite:///./data/social_mind.db
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
CORS_ORIGINS=["https://social.voidnode.dev"]
EOF

# Add to Caddyfile (append to existing)
cat | sudo tee -a /etc/caddy/Caddyfile << 'EOF'

social.voidnode.dev {
    handle_path /api/* { reverse_proxy localhost:8000 }
    handle { reverse_proxy localhost:3000 }
}
EOF

sudo systemctl reload caddy

# Start containers
cd docker
docker-compose -f docker-compose.hyperion.yml up -d --build
```
