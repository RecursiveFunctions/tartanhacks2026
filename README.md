# tartanhacks2026
Our AI acts as a social conductor, turning scattered Instagram DMs into perfectly timed, interest-driven meetups

```mermaid
graph TD
    %% Node Definitions
    Dedalus[Dedalus Labs Cloud]
    MetaServers[Instagram Meta Servers]
    PublicURL[friend-roulette.cm-unity.org]
    
    subgraph LocalPC [Local PC - Pop OS]
        TunnelClient[Cloudflared Tunnel]
        
        subgraph PythonProcess [Python main.py]
            Uvicorn[Uvicorn Server Port 8000]
            MCPServer[MCP Server Logic]
            Instagrapi[Instagrapi Library]
        end
        
        LocalLLM[Local LLM - Ollama]
    end

    %% Data Flow
    Dedalus -- "1. Tool Request" --> PublicURL
    PublicURL == "2. Secure Tunnel" ==> TunnelClient
    TunnelClient -- "3. Forward Request" --> Uvicorn
    Uvicorn --> MCPServer
    
    MCPServer -- "4. Logic Check" --> LocalLLM
    LocalLLM -- "5. Decision" --> MCPServer
    
    MCPServer -- "6. API Call" --> Instagrapi
    Instagrapi -- "7. Send DM" --> MetaServers
    
    MetaServers -- "8. Response" --> Instagrapi
    Instagrapi --> MCPServer
    MCPServer -- "9. Success Result" --> Uvicorn
    Uvicorn --> TunnelClient
    TunnelClient == "10. Back to Cloud" ==> PublicURL
    PublicURL --> Dedalus
```


## collaboration
https://docs.google.com/document/d/180wti5qwo47JyqC9-6rBhiVy1hFe3F0L9RHfCtiCptg/edit?tab=t.0

