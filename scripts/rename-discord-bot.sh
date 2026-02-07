#!/bin/bash

# Rename OpenClaw Discord Bot to distinguish from official OpenClaw.ai bot
# Changes bot name and status to avoid confusion

echo "🔄 Renaming Local OpenClaw Bot..."

# Update config to change bot identity
echo "📝 Updating configuration..."

# Change the bot name and status in config
sed -i 's/OpenClaw AI Agent/OpenClaw DevOps Assistant/' /home/lphan/openclaw/config/config.yaml
sed -i 's/🤖 Building containers.../🔧 DevOps Testing.../' /home/lphan/openclaw/config/config.yaml

# Add bot configuration section if it doesn't exist
if ! grep -q "discord:" /home/lphan/openclaw/config/config.yaml; then
  cat >> /home/lphan/openclaw/config/config.yaml << 'EOF'

# Discord Bot Configuration
discord:
  command_prefix: "/devops"
  status: "🔧 DevOps Testing with Qwen3 NVFP4"
  help_description: "Local OpenClaw DevOps bot - using Qwen3-Next-80B-A3B-Instruct-NVFP4"
EOF
else
  # Update existing discord section
  sed -i 's/command_prefix: "\/"/command_prefix: "\/devops"/' /home/lphan/openclaw/config/config.yaml
  sed -i 's/status: "🤖 Building containers..."/status: "🔧 DevOps Testing with Qwen3 NVFP4"/' /home/lphan/openclaw/config/config.yaml
fi

echo "✅ Configuration updated!"
echo ""
echo "🤖 Bot Changes:"
echo "   - Name: OpenClaw DevOps Assistant"
echo "   - Prefix: /devops (instead of /chat)"
echo "   - Status: 🔧 DevOps Testing with Qwen3 NVFP4"
echo ""
echo "🔄 Restarting container to apply changes..."

# Restart the container
cd /home/lphan/openclaw
docker-compose restart

echo "⏳ Waiting for restart..."
sleep 15

# Check if it's running
if docker ps | grep openclaw_openclaw_1 > /dev/null; then
  echo "✅ Bot restarted successfully!"
  echo ""
  echo "📋 New Commands:"
  echo "   /devops ping - Check bot latency"
  echo "   /devops status - Check OpenClaw system status"  
  echo "   /devops chat - Chat with OpenClaw AI"
  echo ""
  echo "🆚 Your bot will now respond to /devops commands!"
else
  echo "❌ Restart failed - check logs with: docker logs openclaw_openclaw_1"
fi

echo "🎉 Renaming complete!"