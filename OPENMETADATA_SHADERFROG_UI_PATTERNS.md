# OpenMetadata & ShaderFrog UI Flow Patterns for API Integration

## Overview

This document details the UI flow patterns from [OpenMetadata](https://open-metadata.org/) and [ShaderFrog](https://shaderfrog.com/2/) that are specifically relevant to API integration workflows. These patterns enhance the user experience for connecting, configuring, and managing third-party API integrations.

**Additional UI patterns are derived from:**
- **Sim**: [`repos/sim`](https://github.com/simstudioai/sim) - Trigger configuration UI, workflow editor
- **Flowise**: [`repos/Flowise`](https://github.com/FlowiseAI/Flowise) - Node configuration, credential management UI
- **Flojoy**: [`repos/flojoy`](https://github.com/flojoy-ai/studio) - Block palette, visual editor

---

## Table of Contents

1. [OpenMetadata Connector UI Patterns](#openmetadata-connector-ui-patterns)
2. [ShaderFrog Visual Composition Patterns](#shaderfrog-visual-composition-patterns)
3. [API Integration UI Flow Design](#api-integration-ui-flow-design)
4. [Connector Browser & Discovery](#connector-browser--discovery)
5. [Configuration UI Patterns](#configuration-ui-patterns)
6. [Visual Feedback & Status Indicators](#visual-feedback--status-indicators)

---

## OpenMetadata Connector UI Patterns

### 1. Connector Discovery & Selection

**Pattern**: Categorized connector browser with search and filtering

**Key Features from OpenMetadata:**
- **100+ Connectors**: Organized by category (API, Database, Messaging, Dashboard, Pipeline, ML Model, Metadata, Search, Storage)
- **Visual Connector Cards**: Each connector shows:
  - Icon/Logo
  - Name and description
  - Category badges
  - Status indicators (Available, Beta, Coming Soon)
  - Quick stats (usage count, popularity)
- **Search & Filter**:
  - Text search across connector names/descriptions
  - Filter by category
  - Filter by connector type (API, Database, etc.)
  - Sort by popularity, name, or recently added

**UI Flow:**
```
Connector Browser
  ├── Search Bar (with autocomplete)
  ├── Category Filters (sidebar)
  │   ├── API
  │   ├── Database
  │   ├── Messaging
  │   ├── Dashboard
  │   └── Storage
  ├── Connector Grid
  │   ├── Connector Card
  │   │   ├── Icon
  │   │   ├── Name
  │   │   ├── Description
  │   │   ├── Category Badge
  │   │   ├── Status Badge
  │   │   └── "Connect" Button
  │   └── ...
  └── Pagination/Load More
```

### 2. Connector Setup Wizard

**Pattern**: Step-by-step guided setup with validation

**Key Features:**
- **Multi-Step Wizard**:
  1. **Connector Selection**: Choose connector type
  2. **Configuration**: Fill in connection details
  3. **Authentication**: OAuth flow or credential setup
  4. **Test Connection**: Validate configuration
  5. **Metadata Ingestion**: Configure what to sync
  6. **Schedule**: Set up sync frequency
  7. **Review & Deploy**: Final review before activation

**UI Components:**
```typescript
interface ConnectorSetupWizard {
  steps: ConnectorSetupStep[]
  currentStep: number
  config: ConnectorConfig
  validation: ValidationResult
}

interface ConnectorSetupStep {
  id: string
  title: string
  description: string
  component: React.ComponentType<StepProps>
  validation?: (config: ConnectorConfig) => ValidationResult
  canProceed: (config: ConnectorConfig) => boolean
}
```

### 3. Connector Status & Monitoring

**Pattern**: Real-time status dashboard with health indicators

**Key Features:**
- **Status Indicators**:
  - 🟢 Connected & Healthy
  - 🟡 Warning (rate limits, token expiry soon)
  - 🔴 Error (connection failed, token expired)
  - ⚪ Not Configured
- **Health Metrics**:
  - Last successful sync
  - Sync frequency
  - Error rate
  - API call count
  - Rate limit usage
- **Quick Actions**:
  - Test connection
  - Re-authenticate
  - View logs
  - Pause/Resume sync

### 4. Metadata Graph Visualization

**Pattern**: Visual representation of data lineage and relationships

**Key Features:**
- **Graph View**: Interactive node-based visualization
- **Relationship Lines**: Shows data flow between connectors
- **Node Types**: Different visual styles for:
  - APIs
  - Databases
  - Transformations
  - Destinations
- **Lineage Tracking**: Visual path from source to destination

**UI Flow:**
```
Metadata Graph View
  ├── Zoom/Pan Controls
  ├── Node Selection
  │   ├── Details Panel (sidebar)
  │   ├── Properties View
  │   └── Lineage View
  ├── Relationship Lines
  │   ├── Data Flow (arrows)
  │   ├── Dependencies (dotted)
  │   └── Transformations (dashed)
  └── Filter/Search
      ├── By Connector Type
      ├── By Status
      └── By Data Flow Path
```

---

## ShaderFrog Visual Composition Patterns

### 1. Node-Based Visual Editor

**Pattern**: Drag-and-drop node composition with real-time preview

**Key Features:**
- **Node Palette**: Categorized nodes in sidebar
  - Input nodes (textures, constants)
  - Processing nodes (operations, filters)
  - Output nodes (final shader)
- **Canvas Interaction**:
  - Drag nodes from palette
  - Connect nodes with edges
  - Real-time parameter adjustment
  - Visual preview window
- **Node Configuration**:
  - Inline parameter controls
  - Color pickers
  - Sliders for numeric values
  - Dropdowns for options

**UI Flow:**
```
Shader Editor
  ├── Sidebar (Node Palette)
  │   ├── Search
  │   ├── Categories
  │   │   ├── Inputs
  │   │   ├── Math
  │   │   ├── Effects
  │   │   └── Outputs
  │   └── Node List
  ├── Canvas (ReactFlow)
  │   ├── Nodes (draggable)
  │   ├── Edges (connections)
  │   └── Selection
  ├── Properties Panel
  │   ├── Node Properties
  │   ├── Parameter Controls
  │   └── Preview
  └── Preview Window
      └── Real-time Render
```

### 2. Parameter Tweaking Interface

**Pattern**: Real-time parameter adjustment with immediate visual feedback

**Key Features:**
- **Inline Controls**: Parameters visible directly on nodes
- **Real-time Updates**: Changes reflect immediately
- **Visual Feedback**: Preview updates as you adjust
- **Parameter Types**:
  - Numeric sliders
  - Color pickers
  - Toggle switches
  - Dropdown selects
  - Vector inputs

**Applicable to API Integration:**
```typescript
interface APIConnectorNode {
  // Node visual representation
  position: { x: number, y: number }
  type: 'connector'
  
  // Inline parameter controls
  parameters: {
    endpoint: {
      type: 'select',
      value: string,
      options: string[],
      onChange: (value: string) => void
    },
    method: {
      type: 'select',
      value: 'GET' | 'POST' | 'PUT' | 'DELETE',
      onChange: (value: string) => void
    },
    headers: {
      type: 'json-editor',
      value: Record<string, string>,
      onChange: (value: Record<string, string>) => void
    }
  }
  
  // Real-time preview
  preview: {
    url: string
    method: string
    sampleResponse?: any
  }
}
```

### 3. Visual Composition Patterns

**Pattern**: Compose complex workflows from simple building blocks

**Key Features:**
- **Node Categories**: Visual organization by function
- **Connection Validation**: Type-safe connections
- **Visual Feedback**: 
  - Connection highlights
  - Error indicators
  - Success states
- **Nested Composition**: Groups and sub-flows

---

## API Integration UI Flow Design

### Combined Pattern: Connector Browser + Visual Editor

**Inspired by**: OpenMetadata's connector discovery + ShaderFrog's visual composition

**UI Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Connector Browser                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Search       │  │ Categories   │  │ Sort/Filter  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Google   │  │ Slack    │  │ GitHub   │  │ Stripe   │    │
│  │ Calendar │  │          │  │          │  │          │    │
│  │ 📅       │  │ 💬       │  │ 🔧       │  │ 💳       │    │
│  │ [Connect]│  │ [Connect]│  │ [Connect]│  │ [Connect]│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Setup Wizard                               │
│  Step 1: Configuration                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Endpoint: [Select: listEvents / createEvent / ...]     │ │
│  │ Method:   [GET ▼]                                      │ │
│  │ Params:   [JSON Editor]                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Step 2: Authentication                                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [OAuth 2.0 Connect Button]                              │ │
│  │ or                                                       │ │
│  │ API Key: [••••••••••••••] [Show]                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Step 3: Test Connection                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [Test Connection] [✅ Success]                         │ │
│  │ Response Preview: {...}                                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Visual Flow Editor                         │
│  ┌──────────────┐                                            │
│  │ Node Palette │  ┌────────────────────────────────────┐  │
│  │              │  │         Canvas                      │  │
│  │ Connectors   │  │  ┌─────────┐      ┌─────────┐     │  │
│  │   Google     │  │  │ Google   │──────│ Slack   │     │  │
│  │   Calendar   │  │  │ Calendar │      │ Message │     │  │
│  │   [Drag]     │  │  │ Node     │      │ Node    │     │  │
│  │              │  │  └─────────┘      └─────────┘     │  │
│  │ Blocks       │  │                                      │  │
│  │   Condition  │  │  [Properties Panel]                 │  │
│  │   Transform  │  │  Endpoint: listEvents               │  │
│  │              │  │  Method: GET                        │  │
│  │ Triggers     │  │  Params: {...}                      │  │
│  │   Webhook    │  │  [Preview Response]                │  │
│  │   Schedule   │  └────────────────────────────────────┘  │
│  └──────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

### 1. Connector Discovery Flow

**Step-by-Step UI Flow:**

1. **Landing Page** → Shows popular connectors
   - Search bar
   - Category filters
   - Featured connectors

2. **Search/Filter** → User searches for connector
   - Autocomplete suggestions
   - Filter by category, type, authentication method
   - Sort by popularity, recently added, name

3. **Connector Card** → Click on connector
   - Modal/Sidebar with details
   - Description, use cases, examples
   - Authentication requirements
   - Setup instructions
   - "Add to Flow" button

4. **Add to Canvas** → Drag or click to add
   - Connector node appears on canvas
   - Default configuration panel opens
   - Ready for configuration

### 2. Configuration Flow

**Step-by-Step UI Flow:**

1. **Node Selection** → Click on connector node
   - Properties panel opens
   - Shows current configuration
   - Available endpoints/actions

2. **Endpoint Selection** → Choose API endpoint
   - Dropdown with available endpoints
   - Description and parameters shown
   - Sample request/response preview

3. **Parameter Configuration** → Fill in parameters
   - Inline controls (similar to ShaderFrog)
   - Real-time validation
   - Type hints and autocomplete
   - Variable substitution support

4. **Authentication** → Configure credentials
   - OAuth: "Connect Account" button
   - API Key: Secure input field
   - Credential selector if multiple exist

5. **Test Connection** → Validate configuration
   - "Test" button
   - Real-time status indicator
   - Response preview
   - Error messages if failed

6. **Save Configuration** → Persist settings
   - Auto-save or explicit save button
   - Validation before saving
   - Success confirmation

### 3. Visual Composition Flow

**Step-by-Step UI Flow:**

1. **Drag Connector** → From palette to canvas
   - Node appears at drop location
   - Default size and style
   - Ready for connection

2. **Connect Nodes** → Drag from output to input
   - Connection line appears
   - Type validation (green = valid, red = invalid)
   - Visual feedback on hover

3. **Configure Chain** → Set up data flow
   - Each node configurable independently
   - Data transforms between nodes
   - Variable passing via connections

4. **Real-time Preview** → See workflow structure
   - Visual representation
   - Connection validation
   - Error highlighting

5. **Execute/Test** → Run workflow
   - Execution status per node
   - Data flow visualization
   - Result preview

---

## Connector Browser & Discovery

### UI Components

```typescript
// Connector Browser Component
interface ConnectorBrowser {
  connectors: Connector[]
  searchQuery: string
  selectedCategory: string
  sortBy: 'popularity' | 'name' | 'recent'
  
  // Filters
  filters: {
    category: ConnectorCategory[]
    authType: AuthType[]
    status: ConnectorStatus[]
  }
  
  // UI State
  viewMode: 'grid' | 'list'
  selectedConnector: Connector | null
}

// Connector Card Component
interface ConnectorCard {
  connector: Connector
  onClick: () => void
  onConnect: () => void
  
  // Visual Elements
  icon: string | ReactNode
  name: string
  description: string
  category: ConnectorCategory
  status: ConnectorStatus
  popularity: number
  usageCount: number
  
  // Badges
  badges: {
    featured?: boolean
    new?: boolean
    beta?: boolean
    verified?: boolean
  }
}
```

### Visual Design (OpenMetadata-inspired)

**Connector Card Layout:**
```
┌─────────────────────────────┐
│  [Icon]  Google Calendar    │
│          📅                  │
│  Productivity • API          │
│                             │
│  Integrate with Google      │
│  Calendar API to manage     │
│  events and schedules       │
│                             │
│  🔌 OAuth 2.0               │
│  ⭐ 4.8  •  Used 1,234x     │
│                             │
│  [Connect] [View Details]   │
└─────────────────────────────┘
```

---

## Configuration UI Patterns

### 1. Inline Parameter Controls (ShaderFrog-style)

**Pattern**: Parameters visible directly on node with real-time updates

```typescript
interface ConnectorNodeUI {
  // Node visual
  node: {
    id: string
    type: 'connector'
    position: { x: number, y: number }
    selected: boolean
  }
  
  // Inline controls
  parameters: {
    endpoint: ParameterControl
    method: ParameterControl
    headers: ParameterControl
    body: ParameterControl
  }
  
  // Real-time preview
  preview: {
    request: {
      url: string
      method: string
      headers: Record<string, string>
      body?: any
    }
    response?: {
      status: number
      data: any
      timestamp: Date
    }
  }
}

interface ParameterControl {
  type: 'select' | 'input' | 'json-editor' | 'slider' | 'toggle'
  label: string
  value: any
  onChange: (value: any) => void
  validation?: ValidationRule[]
  helperText?: string
  placeholder?: string
}
```

### 2. Configuration Wizard (OpenMetadata-style)

**Pattern**: Multi-step guided setup

```typescript
interface ConnectorSetupWizard {
  connector: Connector
  steps: WizardStep[]
  currentStep: number
  config: Partial<ConnectorConfig>
  
  // Navigation
  onNext: () => void
  onBack: () => void
  onCancel: () => void
  onComplete: (config: ConnectorConfig) => Promise<void>
}

interface WizardStep {
  id: string
  title: string
  description: string
  component: React.ComponentType<WizardStepProps>
  
  // Validation
  validate: (config: Partial<ConnectorConfig>) => ValidationResult
  canProceed: (config: Partial<ConnectorConfig>) => boolean
  
  // UI
  isComplete: boolean
  hasError: boolean
  errorMessage?: string
}
```

### 3. Real-time Preview (ShaderFrog-style)

**Pattern**: Live preview of API request/response

```typescript
interface APIPreview {
  // Request preview
  request: {
    method: string
    url: string
    headers: Record<string, string>
    queryParams?: Record<string, string>
    body?: any
  }
  
  // Response preview
  response?: {
    status: number
    statusText: string
    headers: Record<string, string>
    body: any
    executionTime: number
  }
  
  // Test functionality
  test: () => Promise<void>
  isLoading: boolean
  error?: Error
}
```

---

## Visual Feedback & Status Indicators

### 1. Connection Status (OpenMetadata-style)

**Pattern**: Visual status indicators for connector health

```typescript
interface ConnectorStatus {
  connection: 'connected' | 'disconnected' | 'error' | 'warning'
  lastSync: Date | null
  syncFrequency: string
  errorRate: number
  apiCalls: {
    total: number
    successful: number
    failed: number
    rateLimited: number
  }
  
  // Visual indicators
  statusIcon: ReactNode
  statusColor: string
  statusText: string
}
```

**UI Components:**
- 🟢 **Connected**: Green indicator, "Connected" text
- 🟡 **Warning**: Yellow indicator, "Token expires soon" text
- 🔴 **Error**: Red indicator, "Connection failed" text
- ⚪ **Not Configured**: Gray indicator, "Not configured" text

### 2. Execution Status (ShaderFrog-style)

**Pattern**: Real-time visual feedback during workflow execution

```typescript
interface ExecutionStatus {
  nodeId: string
  status: 'pending' | 'running' | 'success' | 'error' | 'skipped'
  progress?: number // 0-100
  startTime?: Date
  endTime?: Date
  error?: Error
  
  // Visual feedback
  statusIcon: ReactNode
  statusColor: string
  pulseAnimation?: boolean // For running state
}
```

**Visual States:**
- ⚪ **Pending**: Gray, static
- 🔵 **Running**: Blue, pulsing animation
- 🟢 **Success**: Green, checkmark icon
- 🔴 **Error**: Red, X icon with error message
- ⚪ **Skipped**: Gray, dash icon

---

## Implementation Recommendations

### 1. Connector Browser UI

```typescript
// components/connectors/ConnectorBrowser.tsx
export function ConnectorBrowser() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string | null>(null)
  const [connectors, setConnectors] = useState<Connector[]>([])
  
  return (
    <div className="connector-browser">
      {/* Search & Filters */}
      <div className="browser-header">
        <SearchInput value={search} onChange={setSearch} />
        <CategoryFilter value={category} onChange={setCategory} />
        <SortSelector />
      </div>
      
      {/* Connector Grid */}
      <div className="connector-grid">
        {filteredConnectors.map(connector => (
          <ConnectorCard
            key={connector.id}
            connector={connector}
            onClick={() => openConnectorDetails(connector)}
            onConnect={() => startSetupWizard(connector)}
          />
        ))}
      </div>
    </div>
  )
}
```

### 2. Visual Editor Integration

```typescript
// components/editor/ConnectorNode.tsx
export function ConnectorNode({ node }: { node: Node }) {
  const [config, setConfig] = useState(node.data.config)
  const [preview, setPreview] = useState<APIPreview | null>(null)
  
  return (
    <div className="connector-node">
      {/* Node Header */}
      <div className="node-header">
        <Icon name={node.data.connector.icon} />
        <span>{node.data.connector.name}</span>
        <StatusIndicator status={node.data.status} />
      </div>
      
      {/* Inline Parameters (ShaderFrog-style) */}
      <div className="node-parameters">
        <ParameterControl
          label="Endpoint"
          type="select"
          value={config.endpoint}
          options={node.data.connector.endpoints}
          onChange={(value) => updateConfig({ endpoint: value })}
        />
        
        <ParameterControl
          label="Method"
          type="select"
          value={config.method}
          options={['GET', 'POST', 'PUT', 'DELETE']}
          onChange={(value) => updateConfig({ method: value })}
        />
      </div>
      
      {/* Real-time Preview */}
      {preview && (
        <div className="node-preview">
          <PreviewPanel preview={preview} />
          <TestButton onClick={handleTest} />
        </div>
      )}
    </div>
  )
}
```

### 3. Setup Wizard

```typescript
// components/connectors/ConnectorSetupWizard.tsx
export function ConnectorSetupWizard({ connector }: Props) {
  const [step, setStep] = useState(0)
  const [config, setConfig] = useState<Partial<ConnectorConfig>>({})
  
  const steps = [
    { id: 'select-endpoint', component: EndpointSelector },
    { id: 'configure-params', component: ParameterConfig },
    { id: 'authenticate', component: AuthenticationSetup },
    { id: 'test', component: ConnectionTest },
    { id: 'review', component: ReviewAndDeploy }
  ]
  
  return (
    <Wizard>
      <WizardHeader steps={steps} currentStep={step} />
      <WizardContent>
        {steps[step].component({ config, setConfig })}
      </WizardContent>
      <WizardFooter>
        <Button onClick={handleBack} disabled={step === 0}>Back</Button>
        <Button onClick={handleNext} disabled={!canProceed(step, config)}>
          {step === steps.length - 1 ? 'Deploy' : 'Next'}
        </Button>
      </WizardFooter>
    </Wizard>
  )
}
```

---

## Key UI Patterns Summary

### From OpenMetadata:

1. **Connector Discovery**
   - Categorized browser with 100+ connectors
   - Search and filter capabilities
   - Visual connector cards with status indicators
   - Popularity and usage metrics

2. **Setup Wizard**
   - Multi-step guided configuration
   - Step-by-step validation
   - Test connection before deploying
   - Review and confirm before activation

3. **Status Dashboard**
   - Real-time health indicators
   - Last sync information
   - Error rate and API usage metrics
   - Quick action buttons

4. **Metadata Graph**
   - Visual representation of relationships
   - Interactive node-based view
   - Lineage tracking visualization

### From ShaderFrog:

1. **Visual Composition**
   - Drag-and-drop node placement
   - Real-time parameter adjustment
   - Visual preview of results
   - Node categories and organization

2. **Inline Controls**
   - Parameters visible on nodes
   - Real-time updates
   - Type-appropriate controls (sliders, pickers, dropdowns)

3. **Real-time Feedback**
   - Immediate visual updates
   - Preview window
   - Error highlighting
   - Success indicators

---

## Integration into Existing System

### Updated Connector Structure

```typescript
// Enhanced with UI patterns
export interface ConnectorConfig {
  // ... existing fields ...
  
  // UI Configuration
  ui: {
    // Browser display
    card: {
      icon: string
      color: string
      category: ConnectorCategory
      badges: string[]
      featured?: boolean
    }
    
    // Setup wizard
    wizard: {
      steps: WizardStepConfig[]
      defaultValues: Record<string, any>
      validation: ValidationRules
    }
    
    // Node display
    node: {
      icon: string
      color: string
      defaultSize: { width: number, height: number }
      parameterControls: ParameterControlConfig[]
    }
    
    // Preview
    preview: {
      enabled: boolean
      sampleRequest?: any
      sampleResponse?: any
    }
  }
}
```

---

## Related Documentation

- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for complete architecture
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for connector structure
- **Integration Flow**: See `THIRD_PARTY_API_INTEGRATION_FLOW_EXPLAINED.md` for flow explanation
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for visual diagrams

---

## References

- **OpenMetadata**: https://open-metadata.org/ - Unified metadata platform with 100+ connectors
- **ShaderFrog**: https://shaderfrog.com/2/ - Visual shader editor with node-based composition
- **OpenMetadata Connectors**: https://open-metadata.org/docs/connectors - Connector documentation
- **OpenMetadata Architecture**: https://open-metadata.org/docs/architecture - System architecture

---

## Related Documentation

- **Best Integration Approach**: See `BEST_API_INTEGRATION_APPROACH.md` for recommended approach incorporating these UI patterns
- **Production System Design**: See `PRODUCTION_SYSTEM_DESIGN.md` for UI flows implementation with code examples
- **Third-Party API Structure**: See `THIRD_PARTY_API_STRUCTURE.md` for UI integration patterns in connector structure
- **Integration Patterns**: See `THIRD_PARTY_API_INTEGRATION_PATTERNS.md` for UI flow patterns section
- **Integration Flow**: See `THIRD_PARTY_API_INTEGRATION_FLOW_EXPLAINED.md` for UI flow patterns explanation
- **System Architecture Diagrams**: See `SYSTEM_ARCHITECTURE_DIAGRAMS.md` for UI flow components in architecture
- **Comprehensive System Design**: See `COMPREHENSIVE_SYSTEM_DESIGN.md` for visual patterns overview

---

*UI flow patterns specifically designed for API integration workflows, combining OpenMetadata's connector management with ShaderFrog's visual composition approach.*

