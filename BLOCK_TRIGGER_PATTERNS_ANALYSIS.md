# Block/Trigger UI Patterns Analysis

## Overview
This document summarizes the block-based UI and trigger patterns found in three AI workflow platforms (sim, Flowise, flojoy) and insights from visual programming interfaces (ShaderFrog, OpenMetadata).

---

## 1. Sim (simstudioai/sim)

### Architecture
- **Framework**: Next.js (App Router) with ReactFlow
- **State Management**: Zustand
- **Flow Editor**: ReactFlow with custom node/edge components

### Block/Node Implementation

#### Block Structure
- **Location**: `apps/sim/blocks/` - Block registry system
- **Types**: Defined in `blocks/types.ts`
  - Block categories: `'blocks' | 'tools' | 'triggers'`
  - Sub-block types: 30+ types including:
    - `short-input`, `long-input`, `dropdown`, `combobox`
    - `condition-input`, `trigger-config`, `schedule-config`
    - `oauth-input`, `webhook-config`, `file-upload`
    - `mcp-tool-selector`, `knowledge-base-selector`

#### Block Component
- **File**: `components/workflow-block/workflow-block.tsx`
- **Features**:
  - Custom ReactFlow node component
  - Handles connection points (handles) via `ConnectionBlocks`
  - Supports sub-blocks for complex configuration
  - Preview mode support
  - Diff/version comparison support
  - Collaborative editing via Zustand stores

#### Key Components:
1. **WorkflowBlock** - Main block component
2. **ConnectionBlocks** - Handles connection points (inputs/outputs)
3. **SubBlock** - Configurable sub-components within blocks
4. **WorkflowEdge** - Custom edge rendering
5. **SubflowNode** - Nested workflows (loops/parallels)

### Trigger System

#### Trigger Architecture
- **Location**: `apps/sim/triggers/`
- **Registry**: `triggers/index.ts` - Central trigger registry
- **Types**: Defined in `triggers/types.ts`

#### Trigger Types:
- **Webhook-based**: Slack, GitHub, Airtable, Stripe, Telegram, WhatsApp, Microsoft Teams, Webflow, Google Forms
- **Polling-based**: Gmail, Outlook
- **Subscription-based**: Microsoft Teams Chat

#### Trigger Configuration
- **Component**: `components/trigger-config/trigger-config.tsx`
- **Features**:
  - Modal-based trigger setup
  - OAuth credential support
  - Webhook path configuration
  - Sample payload display
  - Setup instructions

#### Trigger Structure:
```typescript
interface TriggerConfig {
  id: string
  name: string
  provider: string
  configFields: Record<string, TriggerConfigField>
  outputs: Record<string, TriggerOutput>
  webhook?: { method, headers }
  requiresCredentials?: boolean
}
```

### ReactFlow Implementation
- Uses ReactFlow with custom node types
- Custom edge rendering (`WorkflowEdge`)
- Supports nested subflows (loops/parallels)
- Real-time collaboration via Socket.io
- Workflow serialization/deserialization

### State Management
- **Workflow Store**: Zustand store for workflow state
- **SubBlock Store**: Separate store for sub-block values
- **Execution Store**: Execution state tracking
- **Collaborative**: Real-time updates via Socket.io

---

## 2. Flowise (FlowiseAI/Flowise)

### Architecture
- **Framework**: React with Material-UI
- **State Management**: Redux
- **Flow Editor**: ReactFlow

### Block/Node Implementation

#### Node Structure
- **Location**: `packages/components/nodes/` - 600+ node files
- **Custom Node Component**: `CanvasNode.jsx`
- **Node Types**: Custom node types registered in ReactFlow

#### Key Components:
1. **CanvasNode** - Main node wrapper
2. **NodeInputHandler** - Input connection handling
3. **NodeOutputHandler** - Output connection handling
4. **ButtonEdge** - Custom edge with button
5. **StickyNote** - Annotation nodes

#### Node Features:
- Drag-and-drop from sidebar (`AddNodes.jsx`)
- Dynamic input/output handles
- Parameter configuration panels
- Variable support (`{{nodeId.data.instance}}`)
- Node versioning and sync
- Upsert capability for vector stores

### Connection System
- **Connection Logic**: `onConnect` handler in `canvas/index.jsx`
- **Connection Format**: `{{sourceNodeId.data.instance}}`
- **Edge Types**: Button edge with custom styling
- **Validation**: Connection validation via `isValidConnection`

### Canvas Implementation
- **File**: `packages/ui/src/views/canvas/index.jsx`
- **Features**:
  - ReactFlow with `useNodesState` and `useEdgesState`
  - Drag-and-drop from sidebar
  - Copy/paste support (JSON format)
  - Snapping grid (25x25)
  - Background toggle
  - Node sync for updates

### State Management
- **Redux**: Canvas state in Redux store
- **ReactFlow Context**: `ReactFlowContext` for flow instance
- **Dirty State**: Tracks unsaved changes

---

## 3. Flojoy (flojoy-ai/studio & studiolab)

### Architecture
- **Framework**: Electron + React + TypeScript
- **State Management**: Zustand
- **Flow Editor**: ReactFlow

### Block/Node Implementation

#### Block Structure
- **Location**: `src/renderer/components/blocks/`
- **Block Types**: Multiple block type components
  - `default-block.tsx`, `data-block.tsx`, `ctrl-flow-block.tsx`
  - `hardware-block.tsx`, `ai-block.tsx`, `math-block.tsx`
  - `numpy-block.tsx`, `scipy-block.tsx`, `etl-block.tsx`

#### Block Components:
- **NodeWrapper** - Base wrapper for all blocks
- **HandleComponent** - Custom handle rendering
- **BlockLabel** - Block title/name display
- **NodeInput** - Input field components
- **CustomHandle** - Custom connection handles

#### Flow Chart View
- **File**: `src/renderer/routes/flow_chart/FlowChartTabView.tsx`
- **Features**:
  - ReactFlow with custom node types
  - Custom edge rendering
  - Block context menu
  - Block expand menu
  - Gallery modal for examples
  - Command menu (Cmd+K)

### Block System
- **Manifest-based**: Blocks defined in manifest files
- **Block Registry**: `stores/manifest.ts`
- **Block Categories**: AI/ML, Data, Hardware, Visualization, etc.
- **Icon System**: SVG icons per block type

### State Management
- **Zustand Stores**:
  - `flowchart.ts` - Flowchart state
  - `project.ts` - Project state
  - `manifest.ts` - Block manifest
  - `socket.ts` - WebSocket for execution

---

## 4. Common Patterns Across All Platforms

### ReactFlow Usage
All three platforms use **ReactFlow** as the core flow editor:
- Custom node types
- Custom edge types
- Connection handling
- Node positioning/dragging
- Zoom/pan controls

### Block/Node Structure
1. **Block Definition**: Registry/Manifest system
2. **Block Component**: React component for rendering
3. **Connection Handles**: Input/output handles
4. **Configuration**: Sub-components for parameters
5. **State**: Store-based state management

### Connection System
- **Edge Types**: Custom edge components
- **Connection Validation**: Rules for valid connections
- **Data Flow**: Variable references between nodes
- **Serialization**: JSON-based workflow storage

### Trigger Patterns (Sim-specific)
- **Registry-based**: Central trigger registry
- **Webhook Support**: Built-in webhook handling
- **OAuth Integration**: Credential-based triggers
- **Polling**: For services without webhooks
- **Configuration UI**: Modal-based setup

---

## 5. Insights from External Platforms

### ShaderFrog (shaderfrog.com/2/)

**Visual Node Composition**:
- Node-based visual programming interface
- Drag-and-drop node placement
- Real-time parameter adjustment with inline controls
- Visual preview of shader output
- Export to Three.js/Babylon.js

**UI Flow Patterns for API Integration**:
- **Inline Parameter Controls**: Parameters visible directly on nodes (select dropdowns, input fields, sliders)
- **Real-time Updates**: Changes reflect immediately in preview
- **Visual Feedback**: Status indicators, connection highlights, error states
- **Node Categories**: Organized palette (Inputs, Math, Effects, Outputs)
- **Visual Composition**: Compose complex workflows from simple building blocks

**Relevant Patterns**:
- Node-based visual programming
- Parameter adjustment interface with inline controls
- Real-time preview of API requests/responses
- Visual feedback during configuration
- Categorized node organization

### OpenMetadata (open-metadata.org/)

**Connector Architecture**:
- 100+ data connectors with standardized pattern
- Unified metadata graph for relationship visualization
- Connector browser UI with search and filtering
- Status dashboard with health indicators
- Lineage visualization for data flow tracking

**UI Flow Patterns for API Integration**:
- **Connector Discovery**: Categorized browser (API, Database, Messaging, Dashboard, Pipeline, ML Model, Metadata, Search, Storage)
- **Visual Connector Cards**: Icons, descriptions, status badges, popularity metrics
- **Setup Wizard**: Multi-step guided configuration with validation
- **Status Dashboard**: Real-time health indicators (🟢🟡🔴), last sync, API metrics
- **Metadata Graph**: Interactive visualization of connector relationships and data flow
- **Quick Actions**: Test connection, re-authenticate, view logs from dashboard

**Relevant Patterns**:
- Connector browser UI for discovery and selection
- Multi-step setup wizard for configuration
- Status dashboard for monitoring and management
- Metadata relationship visualization
- Lineage tracking for data flow
- Unified graph structure for all integrations

**Key Insights for API Integration**:
- OpenMetadata's connector browser provides excellent UX for discovering and connecting APIs
- The setup wizard pattern ensures proper configuration before deployment
- Status dashboard enables proactive monitoring of API integrations
- Metadata graph visualization helps understand integration relationships

---

## 6. Recommended Architecture for CrewAI-like System

### Core Components

#### 1. Flow Editor
- **Library**: ReactFlow (proven in all three platforms)
- **Custom Nodes**: Define CrewAI agent nodes
- **Custom Edges**: Task/workflow connections
- **Zoom/Pan**: Standard ReactFlow controls

#### 2. Block System
```
blocks/
  ├── registry.ts          # Block registry
  ├── types.ts            # Type definitions
  ├── agents/             # Agent blocks
  ├── tasks/              # Task blocks
  ├── tools/              # Tool blocks
  └── triggers/           # Trigger blocks
```

#### 3. Trigger System
- **Registry-based**: Similar to sim's approach
- **Webhook Support**: For external triggers
- **Schedule Support**: Cron-based scheduling
- **Event-based**: For real-time triggers
- **Configuration UI**: Modal/panel for setup

#### 4. State Management
- **Zustand**: Recommended (used by sim & flojoy)
- **Stores**:
  - Workflow store
  - Block store
  - Execution store
  - Trigger store

#### 5. Connection System
- **Handle Types**: Input/output handles per block type
- **Validation**: Type checking for connections
- **Data Flow**: Variable passing between blocks
- **Visual Feedback**: Connection state indicators

### Key Features to Implement

1. **Block Types**:
   - Agent blocks (with role, goal, backstory)
   - Task blocks (with description, expected output)
   - Tool blocks (with tool configuration)
   - Trigger blocks (with trigger configuration)

2. **Trigger Types**:
   - API triggers (webhook)
   - Schedule triggers (cron)
   - Event triggers (real-time)
   - Manual triggers (button)

3. **UI Components**:
   - Block configuration panel
   - Trigger setup modal
   - Connection validation
   - Execution status indicators
   - Error handling display

4. **State Management**:
   - Workflow serialization
   - Block state persistence
   - Execution state tracking
   - Real-time collaboration (optional)

---

## 7. Implementation Recommendations

### Phase 1: Core Flow Editor
1. Set up ReactFlow
2. Create basic block components
3. Implement connection system
4. Add drag-and-drop

### Phase 2: Block System
1. Create block registry
2. Implement block types
3. Add configuration panels
4. Implement validation

### Phase 3: Trigger System
1. Create trigger registry
2. Implement webhook triggers
3. Add schedule triggers
4. Build trigger configuration UI

### Phase 4: Execution
1. Implement workflow execution
2. Add status indicators
3. Error handling
4. Logging

### Phase 5: Advanced Features
1. Real-time collaboration
2. Version control
3. Templates/gallery
4. Export/import

---

## 8. File Structure Example

```
src/
├── components/
│   ├── blocks/
│   │   ├── AgentBlock.tsx
│   │   ├── TaskBlock.tsx
│   │   ├── ToolBlock.tsx
│   │   └── TriggerBlock.tsx
│   ├── edges/
│   │   └── CustomEdge.tsx
│   └── panels/
│       ├── BlockConfigPanel.tsx
│       └── TriggerConfigModal.tsx
├── stores/
│   ├── workflow.ts
│   ├── blocks.ts
│   ├── triggers.ts
│   └── execution.ts
├── blocks/
│   ├── registry.ts
│   ├── types.ts
│   └── definitions/
├── triggers/
│   ├── registry.ts
│   ├── types.ts
│   └── definitions/
└── lib/
    ├── reactflow/
    └── serialization/
```

---

## Conclusion

All three platforms demonstrate successful implementations of block-based visual programming with ReactFlow. The key patterns to adopt:

1. **ReactFlow** as the core editor
2. **Registry-based** block/trigger systems
3. **Zustand** for state management
4. **Custom node/edge** components
5. **Configuration panels** for block setup
6. **Trigger system** with webhook support

The sim platform provides the most comprehensive trigger system, while Flowise demonstrates excellent node management, and Flojoy shows clean block organization. Combining these patterns with CrewAI's agent/task model will create a powerful visual workflow builder.

---

## 9. Semantic Routing Patterns (umbrella_corp)

### Architecture
- **Pattern**: Semantic-router library for intelligent query routing
- **Approach**: Route user queries to appropriate flows/tools using embeddings
- **Hierarchical**: Two-level routing (flow → tool)

### Implementation

#### Semantic Router
```python
# umbrella_corp pattern
class IntelligentRouter:
    def __init__(self, name_of_router, open_ai_api_key):
        self.router = SemanticRouter(
            encoder=OpenAIEncoder(openai_api_key),
            routes=self.get_routes(),
            auto_sync="local"
        )
    
    def get_routes(self, file_name):
        # Load routes from JSON file
        routes = []
        for route in routes_list:
            routes.append(Route(
                name=route["name"],
                utterances=route["utterances"]
            ))
        return routes
```

#### Route Maps
- **Location**: JSON files with utterances and flow mappings
- **Structure**: Each route defines tool name and matching utterances
- **Modifiers**: Support for dynamic utterance generation (e.g., codes lists)

#### Flow-Based Execution
```python
# umbrella_corp pattern
class GoogleSuiteFlow(Flow):
    def process_user_request(self):
        router = self.get_router(self.state.crew_name)
        result = router(self.state.user_query)
        tool_name = result.name
        
        # Execute with specialized crew
        crew = self.googlesuite_crew.create_specialized_crew(tool_name)
        return crew.kickoff(inputs={"user_query": self.state.user_query})
```

### Key Patterns
1. **Route Map Files**: JSON-based route definitions
2. **Utterance Matching**: Keywords/phrases for semantic matching
3. **Flow Hierarchy**: Top-level flows contain multiple tools
4. **Tool Wrapping**: APIs wrapped as CrewAI tools
5. **Dynamic Routing**: Semantic router selects appropriate tool

---

## Related Documentation

- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for production-ready semantic routing implementation
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for route map structure and tool wrapper patterns
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for semantic routing flow diagrams

