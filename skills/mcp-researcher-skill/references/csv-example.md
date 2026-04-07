# CSV Report Example — Telnyx MCP Server (Complete Reference)

> This file is the formatting reference for CSV reports. See SKILL.md for rules and workflow.

```csv
Category,Attribute,Status
MCP Info,Description,"Telnyx MCP Server connects AI agents with Telnyx telephony, messaging, and AI assistant workflows. It provides 50+ tools across SMS/MMS messaging, voice call control, AI assistant creation, cloud storage (S3-compatible), embeddings, webhook management, and integration secrets handling. Supports selective tool filtering and webhook receivers via ngrok integration."
MCP Info,Git Repo Version,"v0.1.2"
MCP Info,Category,"Developer and Coding Tools"
MCP Info,GitHub Repository,"https://github.com/team-telnyx/telnyx-mcp-server"
MCP Info,Endpoint URL,"N/A"
Distribution Type,Official,Yes
Distribution Type,Community,No
MCP Protocol Version,2025-11-25,No
MCP Protocol Version,2025-06-18,Yes
MCP Protocol Version,2025-03-26,No
MCP Protocol Version,2024-11-05,No
Pricing,Free,Yes
Pricing,Paid,No
Hosting Provider,SaaS Vendor,No
Hosting Provider,3rd Party SaaS,No
Hosting Provider,GitHub,Yes
Hosting Provider,GitLab,No
Hosting Provider,Bitbucket,No
Hosting Provider,SourceHut/Gitea/Gogs,No
Authentication,OAuth 2.1 - Authorization Code Flow,No
Authentication,OAuth 2.1 - Client Credentials Flow,No
Authentication,Bearer Token,No
Authentication,Personal Access Token,No
Authentication,API Token,Yes
Data Protection,TLS 1.3,No
Data Protection,TLS 1.2,No
Data Protection,Lower versions or no encryption,No
Transport Protocol,STDIO,Yes
Transport Protocol,HTTP/SSE,No
Transport Protocol,StreamableHttp,No
Transport Protocol,FastAPI,No
Tools Operations,Read-only operations,No
Tools Operations,Read-only and/or update operations,No
Tools Operations,Read-only update and/or delete operations,Yes
Deployment Approach,Local,Yes
Deployment Approach,Container,No
Deployment Approach,Remote,No
Compliance & Certifications,HIPAA,No
Compliance & Certifications,GDPR,No
Compliance & Certifications,SOC 2,No
Compliance & Certifications,FedRAMP,No
Capabilities,Tools,Yes
Capabilities,Resources,Yes
Capabilities,Prompts,No
Capabilities,Sampling,No
Capabilities - Tools,detailed_info,"Search & Query Utilities
  • list_assistants – List all existing AI assistants
  • get_assistant – Get details for a specific AI assistant
  • get_assistant_texml – Get TEXML configuration for an assistant
  • list_call_control_applications – List call control applications
  • get_call_control_application – Get details for a call control application
  • get_message – Get details for a specific message
  • sms_conversations – Access and view ongoing SMS conversations
  • list_phone_numbers – List all phone numbers on the account
  • list_available_numbers – Search for available phone numbers by area code or pattern
  • list_connections – List voice connections configured on the account
  • get_connection – Get details for a specific connection
  • cloud_storage_list_buckets – List all storage buckets across all regions
  • cloud_storage_list_objects – List objects in a bucket
  • cloud_storage_get_bucket_location – Get bucket location information
  • list_embedded_buckets – List existing embedded buckets
  • list_secrets – List integration secrets

Admin & Miscellaneous
  • webhook_configuration – Configure webhook receivers for Telnyx events
  • webhook_management – Manage active webhooks via ngrok integration
  • create_secret – Create new bearer or basic auth secrets
  • delete_secret – Delete integration secrets

Other
  • create_assistant – Create a new AI assistant with custom instructions and configurations
  • update_assistant – Update an existing assistant's properties and configuration
  • delete_assistant – Delete an AI assistant
  • start_assistant_call – Start an outbound call using an AI assistant
  • make_call – Make an outbound phone call to a destination number
  • hangup – Hang up an active phone call
  • transfer – Transfer an active call to a new destination
  • playback_start – Play audio file or URL during an active call
  • playback_stop – Stop audio playback on an active call
  • send_dtmf – Send DTMF (touch-tone) signals during a call
  • speak – Convert text to speech and play during a call
  • create_call_control_application – Create a new call control application
  • send_message – Send SMS or MMS messages to recipients
  • buy_phone_numbers – Purchase new phone numbers
  • update_phone_numbers – Update phone number configurations
  • update_connection – Update connection configurations
  • cloud_storage_create_bucket – Create a new cloud storage bucket
  • cloud_storage_upload_file – Upload files to a bucket
  • cloud_storage_download_file – Download files from a bucket
  • cloud_storage_delete_object – Delete objects from a bucket
  • scrape_and_embed_url – Scrape website URL and create embeddings for AI training
  • create_file_embeddings – Create embeddings for custom files"
Capabilities - Resources,detailed_info,"API Configuration Resources
  • webhook_receiver – Webhook endpoint configuration (resource type: JSON document)
  • integration_secret – Integration credentials storage (resource type: encrypted document)
  • call_recording – Audio recording artifact (resource type: audio/wav)

Cloud Storage
  • bucket_content – Cloud storage bucket contents (resource type: directory listing)
  • file_object – File object with metadata (resource type: binary/document)
  • embeddings_index – Vector embedding index (resource type: data structure)"
Capabilities - Prompts,detailed_info,"None"
Capabilities - Sampling,detailed_info,"None"
Non-Read-Only Tools,detailed_info,"Import/Export Tools
  • cloud_storage_upload_file: Upload files to a bucket
  • cloud_storage_download_file: Download files from a bucket

Content Management
  • create_assistant: Create a new AI assistant with custom instructions
  • update_assistant: Update an existing assistant's properties
  • delete_assistant: Remove an AI assistant
  • buy_phone_numbers: Purchase new phone numbers
  • update_phone_numbers: Update phone number configurations
  • update_connection: Update connection configurations
  • cloud_storage_create_bucket: Create a new cloud storage bucket
  • cloud_storage_delete_object: Remove objects from a bucket
  • create_secret: Create new bearer or basic auth secrets
  • delete_secret: Remove integration secrets

Configuration Tools
  • webhook_configuration: Configure webhook receivers for Telnyx events
  • webhook_management: Manage active webhooks via ngrok integration

Other Write Operations
  • start_assistant_call: Start an outbound call using an AI assistant
  • make_call: Make an outbound phone call to a destination number
  • hangup: Hang up an active phone call
  • transfer: Transfer an active call to a new destination
  • playback_start: Play audio file or URL during an active call
  • playback_stop: Stop audio playback on an active call
  • send_dtmf: Send DTMF (touch-tone) signals during a call
  • speak: Convert text to speech and play during a call
  • create_call_control_application: Create a new call control application
  • send_message: Send SMS or MMS messages to recipients
  • scrape_and_embed_url: Scrape website URL and create embeddings
  • create_file_embeddings: Create embeddings for custom files"
```
