# Streamlit UI Structure and Navigation Plan

## Overview
This document outlines the user interface structure for the Automated Review Engine's Streamlit application, focusing on user workflow and intuitive navigation for regulatory affairs specialists.

## UI Design Principles

### User-Centric Design
- **Workflow-Oriented**: Follow the natural review process flow
- **Progressive Disclosure**: Show information as needed
- **Clear Feedback**: Provide status updates and progress indicators
- **Error Prevention**: Validate inputs and provide helpful guidance

### Regulatory Compliance Focus
- **Audit Trail**: Track all user actions and decisions
- **Documentation**: Provide help and context throughout
- **Consistency**: Maintain consistent terminology and layout
- **Accessibility**: Support different user skill levels

## Application Structure

### Main Navigation
```
┌─────────────────────────────────────────────────────────────┐
│                     ARE - Navigation                       │
├─────────────────────────────────────────────────────────────┤
│ 🏠 Home | 📁 Setup | 🔍 Review | 📊 Results | ⚙️ Settings │
└─────────────────────────────────────────────────────────────┘
```

### Page Hierarchy
```
Automated Review Engine (ARE)
├── 🏠 Home
│   ├── Dashboard Overview
│   ├── Recent Reviews
│   └── Quick Actions
├── 📁 Setup
│   ├── Document Upload
│   ├── Template Selection
│   ├── Review Script Configuration
│   └── PLM Data Input
├── 🔍 Review
│   ├── Review Configuration
│   ├── Execute Review
│   └── Progress Monitoring
├── 📊 Results
│   ├── Review Report
│   ├── PLM Directions
│   ├── Download Options
│   └── Review History
└── ⚙️ Settings
    ├── Application Settings
    ├── Template Management
    └── Script Management
```

## Detailed Page Designs

### 1. Home Page (`🏠 Home`)
**Purpose**: Welcome users and provide overview of system status

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Automated Review Engine - Welcome                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Dashboard Overview                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Total     │ │   Active    │ │      System Status      │ │
│  │  Reviews    │ │  Sessions   │ │     ✅ Operational      │ │
│  │     15      │ │      2      │ │                         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│                                                             │
│  📋 Recent Reviews                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Date       │ Document        │ Status    │ Actions      │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ 2025-07-21 │ EU_DoC_v2.pdf  │ Complete  │ View Report  │ │
│  │ 2025-07-20 │ Device_Spec.doc │ In Progress│ Continue    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ⚡ Quick Actions                                           │
│  [Start New Review] [View Templates] [System Status]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Components**:
- System status indicators
- Recent review summary
- Quick action buttons
- Navigation to main workflows

### 2. Setup Pages (`📁 Setup`)

#### 2.1 Document Upload
**Purpose**: Upload and validate documents for review

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  📁 Document Upload                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 Document Under Review                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Drag and drop file here or click to browse             │ │
│  │  Supported formats: PDF, MS Word (.docx)                │ │
│  │  Maximum size: 50MB                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ✅ Upload Status                                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 📄 filename.pdf (2.5MB) - Processing...                │ │
│  │ ▓▓▓▓▓▓▓▓░░ 80% Complete                                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📋 Document Information                                    │
│  • File Type: PDF                                          │
│  • Pages: 15                                               │
│  • Text Extracted: Yes                                     │
│  • Structure Detected: 8 sections                          │
│                                                             │
│  [Continue to Template Selection] [Cancel]                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.2 Template Selection
**Purpose**: Select or upload document template

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  📋 Template Selection                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📂 Available Templates                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ○ EU Declaration of Conformity (v2.1)                  │ │
│  │   Medical Device Standard Template                      │ │
│  │   Last Updated: 2025-06-15                             │ │
│  │                                                         │ │
│  │ ○ FDA 510(k) Template (v1.3)                          │ │
│  │   US Market Submission Template                         │ │
│  │   Last Updated: 2025-05-20                             │ │
│  │                                                         │ │
│  │ ○ Upload Custom Template                                │ │
│  │   Browse for MS Word template file                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📄 Template Preview                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Selected: EU Declaration of Conformity (v2.1)          │ │
│  │                                                         │ │
│  │ Expected Sections:                                      │ │
│  │ 1. Product Identification                               │ │
│  │ 2. Regulatory Classification                            │ │
│  │ 3. Conformity Assessment                                │ │
│  │ 4. Applied Standards                                    │ │
│  │ 5. Authorized Representative                            │ │
│  │ 6. Declaration Statement                                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Continue to Review Script] [Back] [Preview Template]     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3 Review Script Configuration
**Purpose**: Configure review parameters and rules

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Review Script Configuration                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📜 Available Scripts                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ○ Standard EU DoC Review (v1.2)                        │ │
│  │   Comprehensive compliance checking                     │ │
│  │                                                         │ │
│  │ ○ Quick Validation Check (v1.0)                        │ │
│  │   Basic structure and content validation               │ │
│  │                                                         │ │
│  │ ○ Custom Script                                         │ │
│  │   Define custom review rules                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ⚙️ Script Parameters                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Validation Level: [Strict ▼]                           │ │
│  │ Check Standards: ☑️ Required  ☑️ Optional              │ │
│  │ PLM Integration: ☑️ Generate search directions         │ │
│  │ Report Format: [Detailed ▼]                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📋 Selected Rules Preview                                  │
│  • Check all required sections present                     │
│  • Validate product identification format                  │
│  • Verify regulatory classification                        │
│  • Check applied standards format                          │
│  • Validate authorized representative info                 │
│                                                             │
│  [Continue to PLM Data] [Back] [Edit Script]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.4 PLM Data Input
**Purpose**: Input or upload PLM system data

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  💾 PLM Data Input                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Data Input Method                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ○ Manual Entry                                          │ │
│  │   Paste data directly into form fields                 │ │
│  │                                                         │ │
│  │ ● CSV File Upload                                       │ │
│  │   Upload CSV file with PLM data                        │ │
│  │   [Browse Files] sample_plm_data.csv                   │ │
│  │                                                         │ │
│  │ ○ Skip PLM Data                                         │ │
│  │   Continue without PLM integration                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📋 PLM Data Preview                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Product ID     │ ABC-12345                              │ │
│  │ Product Name   │ Cardiac Monitor Device                 │ │
│  │ Classification │ Class IIa                              │ │
│  │ Manufacturer   │ Medical Devices Inc.                   │ │
│  │ Model Number   │ CM-2024-Pro                           │ │
│  │ Serial Range   │ 240001-249999                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ✅ Data Validation                                         │
│  • All required fields present                             │
│  • Data format valid                                       │
│  • Cross-references checked                                │
│                                                             │
│  [Start Review] [Back] [Edit Data]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Review Pages (`🔍 Review`)

#### 3.1 Review Execution
**Purpose**: Execute review and monitor progress

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Review Execution - Session #12345                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Review Progress                                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Overall Progress: ▓▓▓▓▓▓▓░░░ 70% Complete               │ │
│  │                                                         │ │
│  │ ✅ Document Processing        Complete                   │ │
│  │ ✅ Template Analysis          Complete                   │ │
│  │ 🔄 Content Validation        In Progress...             │ │
│  │ ⏳ PLM Direction Generation   Pending                    │ │
│  │ ⏳ Report Generation          Pending                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📋 Live Results Preview                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Findings So Far:                                        │ │
│  │                                                         │ │
│  │ ✅ Document structure matches template                  │ │
│  │ ✅ All required sections present                        │ │
│  │ ⚠️  Product ID format needs verification                │ │
│  │ ❌ Missing authorized representative signature          │ │
│  │                                                         │ │
│  │ Current Status: 2 issues found, 8 checks passed        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📈 Performance Metrics                                     │
│  • Processing Time: 1:23 / ~3:00 estimated                │
│  • Rules Checked: 15/23                                    │
│  • Memory Usage: Normal                                     │
│                                                             │
│  [Pause Review] [Cancel] [View Detailed Log]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. Results Pages (`📊 Results`)

#### 4.1 Review Report
**Purpose**: Display comprehensive review results

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Review Report - Session #12345                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📈 Executive Summary                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Document: EU_DoC_Medical_Device.pdf                     │ │
│  │ Template: EU Declaration of Conformity v2.1             │ │
│  │ Review Date: July 21, 2025 15:30                       │ │
│  │                                                         │ │
│  │ Overall Status: ⚠️ REVIEW REQUIRED                      │ │
│  │ Compliance Score: 85/100                                │ │
│  │                                                         │ │
│  │ 📊 Summary:                                             │ │
│  │ • 18 checks passed ✅                                   │ │
│  │ • 3 warnings ⚠️                                        │ │
│  │ • 2 critical issues ❌                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  🔍 Detailed Findings                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ❌ Critical Issues (2)                                  │ │
│  │ ├─ Missing authorized rep signature (Section 5)         │ │
│  │ └─ Invalid classification code format (Section 2)       │ │
│  │                                                         │ │
│  │ ⚠️ Warnings (3)                                         │ │
│  │ ├─ Product ID format inconsistent (Section 1)          │ │
│  │ ├─ Standard reference incomplete (Section 4)            │ │
│  │ └─ Date format non-standard (Section 6)                │ │
│  │                                                         │ │
│  │ ✅ Passed Checks (18)                                   │ │
│  │ ├─ Document structure valid                             │ │
│  │ ├─ All required sections present                        │ │
│  │ └─ [View all passed checks]                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Download Report] [View PLM Directions] [Start New Review]│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 PLM Directions
**Purpose**: Display generated PLM search directions

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 PLM Search Directions                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 Search Instructions                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Based on the review findings, please execute the        │ │
│  │ following searches in your PLM system to gather         │ │
│  │ additional information for compliance verification.      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  🔍 Required Searches                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1. Product Search - High Priority                       │ │
│  │    Search Mode: Product Search                          │ │
│  │    Field: Product ID                                    │ │
│  │    Search String: "ABC-12345"                          │ │
│  │    Purpose: Verify product identification details       │ │
│  │    [Copy Search String]                                 │ │
│  │                                                         │ │
│  │ 2. Document Search - Medium Priority                    │ │
│  │    Search Mode: Document Search                         │ │
│  │    Field: Document Type                                 │ │
│  │    Search String: "Declaration of Conformity"          │ │
│  │    Purpose: Find related compliance documents           │ │
│  │    [Copy Search String]                                 │ │
│  │                                                         │ │
│  │ 3. Item Search - Medium Priority                        │ │
│  │    Search Mode: Item Search                             │ │
│  │    Field: Classification Code                           │ │
│  │    Search String: "Class IIa"                          │ │
│  │    Purpose: Verify regulatory classification            │ │
│  │    [Copy Search String]                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📋 Search Results Tracking                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ □ Product search completed                              │ │
│  │ □ Document search completed                             │ │
│  │ □ Item search completed                                 │ │
│  │ □ All required information gathered                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Download Instructions] [Print] [Email to Team]          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## UI Component Library

### Navigation Components
- **Main Navigation Bar**: Top-level page navigation
- **Breadcrumb Navigation**: Current location within workflow
- **Progress Indicators**: Step-by-step workflow progress
- **Action Buttons**: Primary and secondary actions

### Input Components
- **File Upload Widget**: Drag-and-drop file upload
- **Form Fields**: Text inputs, dropdowns, checkboxes
- **Data Tables**: Editable tables for PLM data
- **Text Areas**: Multi-line text input for scripts

### Display Components
- **Status Cards**: Summary information display
- **Progress Bars**: Task progress indication
- **Data Tables**: Results and findings display
- **Expandable Sections**: Collapsible content areas

### Feedback Components
- **Alerts**: Success, warning, error messages
- **Tooltips**: Contextual help information
- **Modal Dialogs**: Confirmation and detail dialogs
- **Loading Spinners**: Processing indicators

## Responsive Design

### Desktop Layout (1200px+)
- Full sidebar navigation
- Multi-column layouts
- Detailed information panels
- Large upload areas

### Tablet Layout (768px - 1199px)
- Collapsible sidebar
- Two-column layouts
- Condensed information
- Touch-friendly buttons

### Mobile Layout (< 768px)
- Bottom navigation
- Single-column layout
- Essential information only
- Large touch targets

## Accessibility Features

### WCAG 2.1 Compliance
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels
- **Color Contrast**: High contrast text and backgrounds
- **Focus Indicators**: Clear focus indication

### User Experience Enhancements
- **Help System**: Contextual help and tooltips
- **Error Prevention**: Input validation and guidance
- **Progress Saving**: Auto-save functionality
- **Undo/Redo**: Action reversal capability

## Internationalization Preparation

### Text Externalization
- All user-facing text in external files
- Support for multiple languages
- Date and number format localization
- Right-to-left layout support
