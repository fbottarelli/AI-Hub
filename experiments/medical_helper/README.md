# Medical Helper - Personal Health Tracker

A comprehensive Streamlit-based health tracking application that helps you manage your health records, conditions, and medical information in a structured and relational way.

## ✨ Features

### 🏥 Health Conditions Management
- **Create and manage health conditions** (e.g., Hypertension, Diabetes)
- **Track condition status**: Active, Resolved, Chronic, Monitoring
- **Severity levels**: Mild, Moderate, Severe
- **Visual status indicators** with color-coded badges
- **Categorized by medical specialty** (Cardiovascular, Respiratory, etc.)

### 📝 Health Records with Relationships
- **Multiple record types**:
  - 💊 Medications (with dosage, frequency, prescribing doctor)
  - 🤒 Symptoms (with severity, location, duration)
  - 🔬 Health Analysis (lab results, imaging, physical exams)
  - 👩‍⚕️ Appointments (with doctor, clinic, preparation notes)
  - 📝 Daily Notes (mood, energy, sleep quality)
  - 🏥 Treatments (procedures, therapies, outcomes)

### 🔗 Relational Structure
- **Link records to conditions**: Each record can be associated with a specific health condition
- **Visual linking indicators**: Clear badges show linked vs. unlinked records
- **Relationship prompts**: System asks "Is this treatment related to an existing condition?"
- **Unlinked records management**: Dedicated page to organize orphaned records
- **Hierarchical organization**: Conditions → Records → Attachments

### 🎨 Visual Organization
- **Color-coded categories**: Each record type has a distinct color
- **Status badges**: Visual indicators for condition status, severity, and linking
- **Icon system**: Intuitive icons for each record type
- **Responsive design**: Works well on different screen sizes

### 📊 Analytics and Insights
- **Dashboard overview**: Active conditions, recent records, quick stats
- **Category distribution**: Visual breakdown of record types
- **Linked vs. unlinked metrics**: Track data organization progress
- **Condition-specific views**: See all records related to a specific condition

### 🔍 Advanced Search and Filtering
- **Multi-criteria search**: Search by keywords, category, tags, and conditions
- **Condition-based filtering**: View records for specific conditions
- **Unlinked records filter**: Find records that need to be organized
- **Tag-based organization**: Flexible tagging system

### 📎 File Management
- **Attachment support**: Upload PDFs, images, documents
- **Organized storage**: Files stored in structured directories
- **File metadata**: Track file type, size, upload date
- **Link to records**: Attachments associated with specific records

## 🏗️ Technical Architecture

### Session-Based Navigation
- **Persistent page state**: Navigation state maintained across interactions
- **Seamless transitions**: Dashboard buttons and sidebar navigation work consistently
- **Force page changes**: Buttons can programmatically navigate to specific pages
- **State management**: Proper handling of editing states and form submissions

### Backend-Agnostic Design
- **Structured JSON storage**: Separate files for records, conditions, and attachments
- **Modular architecture**: Clear separation between data models and UI
- **Portable data format**: Easy to migrate to different backends
- **Local storage**: Data stored in `health_data/` directory

### Data Structure
```
health_data/
├── records.json         # Health records
├── conditions.json      # Health conditions
├── attachments.json     # File attachments metadata
└── uploads/            # Uploaded files
```

### Models
- **Condition**: Health conditions with status, severity, and relationships
- **HealthRecord**: Individual health records with optional condition linking
- **FileAttachment**: File metadata and storage information
- **HealthRecordManager**: Centralized data management

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- UV (recommended) or pip

### Installation
```bash
# Clone the repository
cd experiments/medical_helper

# Install dependencies (with UV)
uv sync

# Or with pip
pip install -r requirements.txt
```

### Running the Application
```bash
# With UV (recommended)
uv run streamlit run app.py

# Or with regular Python
streamlit run app.py
```

The application will be available at `http://localhost:8502`

### First Time Setup
1. **Start with conditions**: Add your main health conditions first
2. **Add records**: Create health records and link them to conditions
3. **Upload attachments**: Add relevant documents and images
4. **Organize unlinked records**: Use the "Unlinked Records" page to organize orphaned data

## 📱 User Interface

### Navigation
- **Dashboard**: Overview of conditions and recent records with quick action buttons
- **My Conditions**: Manage health conditions with filtering and editing
- **Add New Record**: Create new health records with relationship prompts
- **View All Records**: Browse all records with sorting and filtering
- **Search Records**: Advanced search with condition filtering
- **Unlinked Records**: Organize records not linked to conditions

### Key Workflows
1. **Adding a medication**: 
   - Select medication type → Choose/create condition → Fill details → Save
2. **Linking existing records**:
   - Go to "Unlinked Records" → Select condition → Link record
3. **Condition management**:
   - Add condition → Link related records → Track progress

### Navigation Features
- **Consistent navigation**: Both sidebar and dashboard buttons work seamlessly
- **Context preservation**: Form states and editing modes are maintained
- **Quick actions**: Dashboard provides direct access to common tasks
- **Visual feedback**: Clear indication of current page and available actions

## 🔧 Current Status

### ✅ Completed Features
- [x] Condition management system
- [x] Relational record structure
- [x] Visual categorization and badges
- [x] Relationship prompts during record creation
- [x] Unlinked records management
- [x] Advanced search and filtering
- [x] File attachment system
- [x] Backend-agnostic JSON storage
- [x] Responsive UI design
- [x] Session-based navigation system
- [x] Dashboard quick actions
- [x] Specialized forms for each record type

### 🚧 In Progress
- [ ] Bulk record operations
- [ ] Export functionality
- [ ] Data visualization charts
- [ ] Mobile-optimized interface

## 🛣️ Next Steps

### Phase 1: Enhanced User Experience
- **Bulk operations**: Select multiple records for linking/unlinking
- **Quick actions**: Keyboard shortcuts and bulk operations
- **Better mobile support**: Responsive design improvements
- **Drag-and-drop**: Intuitive record organization

### Phase 2: Data Insights
- **Timeline visualization**: Track condition progression over time
- **Medication adherence**: Track medication schedules and compliance
- **Symptom correlation**: Identify patterns between symptoms and triggers
- **Health metrics dashboard**: Visual charts for key health indicators

### Phase 3: Advanced Features
- **Reminder system**: Medication and appointment reminders
- **Doctor sharing**: Export data for healthcare providers
- **Integration**: Connect with health devices and APIs
- **AI insights**: Automated pattern recognition and suggestions

### Phase 4: Multi-Platform
- **React frontend**: Replace Streamlit with React for better UX
- **Mobile app**: Native mobile application
- **Cloud sync**: Optional cloud storage and sync
- **Multi-user**: Family account management

## 🏥 Medical Categories

The system supports the following medical categories:
- **Cardiovascular**: Heart and blood vessel conditions
- **Respiratory**: Lung and breathing conditions
- **Gastrointestinal**: Digestive system conditions
- **Musculoskeletal**: Bones, joints, and muscles
- **Neurological**: Brain and nervous system conditions
- **Endocrine**: Hormonal and metabolic conditions
- **Dermatological**: Skin conditions
- **Mental Health**: Psychological and psychiatric conditions
- **Infectious Disease**: Bacterial, viral, and other infections
- **Autoimmune**: Immune system disorders
- **Other**: Miscellaneous conditions

## 💡 Usage Tips

### Best Practices
1. **Start with conditions**: Always add your main health conditions first
2. **Use descriptive titles**: Make record titles clear and searchable
3. **Tag consistently**: Use consistent tags for better organization
4. **Link promptly**: Link records to conditions as soon as possible
5. **Upload documents**: Attach relevant medical documents and images
6. **Regular reviews**: Periodically review and update condition status

### Data Organization
- **Symptoms → Conditions**: Start with symptom tracking, then link to diagnoses
- **Medications → Conditions**: Always link medications to the conditions they treat
- **Appointments → Conditions**: Link follow-up appointments to relevant conditions
- **Tests → Conditions**: Link lab results and imaging to specific conditions

### Navigation Tips
- **Use dashboard buttons**: Quick access to common actions from the main dashboard
- **Sidebar navigation**: Use the sidebar for direct page navigation
- **Context awareness**: The app remembers your current task when navigating
- **Unlinked records**: Regularly check and organize unlinked records

## 🔒 Privacy and Security

- **Local storage**: All data stored locally on your device
- **No cloud sync**: No automatic cloud synchronization (optional in future)
- **File encryption**: Consider encrypting sensitive medical documents
- **Regular backups**: Back up your `health_data/` directory regularly

## 🐛 Troubleshooting

### Common Issues
- **Navigation not working**: Ensure you're using the latest version with fixed navigation
- **Records not appearing**: Check if they're properly linked to conditions
- **File uploads failing**: Verify the `health_data/uploads/` directory exists
- **Performance issues**: Consider archiving old records or splitting data

### Recent Fixes
- **Navigation consistency**: Fixed issue where dashboard buttons weren't working properly
- **Session state management**: Improved page state persistence across interactions
- **Form handling**: Better handling of form submissions and page transitions

## 🤝 Contributing

This project is designed to be extensible and welcomes contributions:

1. **Backend adapters**: Add support for different storage backends
2. **New record types**: Add specialized record types for specific medical needs
3. **Visualization**: Add charts and graphs for health data analysis
4. **Integrations**: Connect with health devices and external APIs
5. **UI improvements**: Enhance the user interface and experience

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For questions, suggestions, or issues:
- Check the unlinked records page if data seems missing
- Ensure all conditions are properly configured
- Verify file attachments are in the correct directory
- Review the console for any error messages
- Test navigation using both sidebar and dashboard buttons

---

**Note**: This application is for personal health tracking and should not replace professional medical advice. Always consult with healthcare providers for medical decisions.