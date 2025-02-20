# Tasks to Carry Out

## 1. Database and Field Mapping ✓
- [x] Create table with field IDs from vector database
- [x] Provide example values for each field
- [x] Document field relationships and dependencies
- [x] Validate field mappings against database schema
- [x] Test field availability in queries

## 2. Query Response Formatting ✓
### General Query Responses ✓
- [x] Update response template structure
  - [x] Standardize field order
  - [x] Implement consistent formatting
  - [x] Add metadata section
- [x] Implement field validation
  - [x] Add null value handling
  - [x] Format currency values
  - [x] Format date fields
- [x] Add result pagination
  - [x] Implement page size limits
  - [x] Add next/previous indicators
  - [x] Include total count

### Specific Query Responses ✓
- [x] Enhance detail level
  - [x] Add contractor section
  - [x] Include financial details
  - [x] Add project timeline
  - [x] Include monitoring data
- [x] Implement response validation
  - [x] Check required fields
  - [x] Validate data types
  - [x] Verify formatting

## 3. Debug System Issues
### Server Setup
- [ ] Fix main.py not found error
  - [ ] Verify file location in app directory
  - [ ] Check Python path settings
  - [ ] Validate imports
- [ ] Test database connection
  - [ ] Verify malawi_projects1.db access
  - [ ] Test SQLTracker initialization
  - [ ] Validate query execution
- [ ] Check application flow
  - [ ] Test FastAPI startup
  - [ ] Verify query parser
  - [ ] Test response generator

## 4. Infrastructure Setup
### Subdomain Configuration
- [ ] Create dziwani.kwantu.support
  - [ ] Configure DNS records
  - [ ] Set up SSL certificate
  - [ ] Configure hosting environment
- [ ] Clone RAG SQL tab
  - [ ] Copy required components
  - [ ] Update configuration
  - [ ] Test functionality

## 5. UI Implementation
### Branding Updates
- [ ] Change title to "Welcome to Dwizani!"
  - [ ] Update header text
  - [ ] Modify font size
  - [ ] Adjust styling
- [ ] Update description
  - [ ] Add Chichewa meaning
  - [ ] Format text
  - [ ] Check responsiveness

### Layout Optimization
- [ ] Make header larger
  - [ ] Adjust font sizes
  - [ ] Update padding
  - [ ] Ensure mobile compatibility
- [ ] Optimize canvas width
  - [ ] Center chat area
  - [ ] Set responsive margins
  - [ ] Test on different screens

### Guidance Tiles
- [ ] Sector Search Box
  - [ ] Design tile layout
  - [ ] Add sector icons
  - [ ] Include example queries
  - [ ] Implement hide/show
- [ ] Location Search Box
  - [ ] List districts/regions
  - [ ] Add map integration
  - [ ] Include example queries
  - [ ] Implement hide/show
- [ ] Specific Project Search
  - [ ] Add project code search
  - [ ] Include name search
  - [ ] Show example formats
  - [ ] Implement hide/show

## 6. LLM Integration Plan (New)
### Phase 1: Preparation
- [ ] Select LLM Provider
  - [ ] Evaluate OpenAI vs Anthropic
  - [ ] Compare pricing models
  - [ ] Test API performance
  - [ ] Assess token limits
- [ ] Design Prompt Engineering
  - [ ] Create base prompts
  - [ ] Develop system messages
  - [ ] Design few-shot examples
  - [ ] Test prompt effectiveness

### Phase 2: Query Understanding
- [ ] Implement Query Classification
  - [ ] Train on existing patterns
  - [ ] Add intent detection
  - [ ] Handle ambiguous queries
  - [ ] Support multi-intent queries
- [ ] Entity Extraction
  - [ ] Project name recognition
  - [ ] Location extraction
  - [ ] Sector classification
  - [ ] Status identification

### Phase 3: Response Generation
- [ ] Natural Language Generation
  - [ ] Design response templates
  - [ ] Implement context awareness
  - [ ] Add explanation generation
  - [ ] Support follow-up queries
- [ ] Response Formatting
  - [ ] Maintain consistent structure
  - [ ] Handle multiple results
  - [ ] Include relevant metadata
  - [ ] Format technical details

### Phase 4: Integration
- [ ] API Integration
  - [ ] Set up API client
  - [ ] Implement rate limiting
  - [ ] Add error handling
  - [ ] Monitor usage
- [ ] Context Management
  - [ ] Design context storage
  - [ ] Implement conversation history
  - [ ] Handle context windows
  - [ ] Manage token limits

### Phase 5: Testing & Optimization
- [ ] Performance Testing
  - [ ] Measure response times
  - [ ] Test concurrent requests
  - [ ] Monitor token usage
  - [ ] Optimize prompts
- [ ] Quality Assurance
  - [ ] Validate responses
  - [ ] Test edge cases
  - [ ] Compare with rule-based
  - [ ] Gather user feedback

## 7. Testing & Validation
### Query Testing
- [ ] Test specific queries
- [ ] Validate general queries
- [ ] Check statistical queries
- [ ] Test edge cases

### UI Testing
- [ ] Validate responsive design
- [ ] Test tile interactions
- [ ] Check animations
- [ ] Verify accessibility

### Performance Testing
- [ ] Measure response times
- [ ] Test concurrent users
- [ ] Monitor resource usage
- [ ] Validate caching

## 8. Documentation
### User Guide
- [ ] Create usage instructions
- [ ] Document query types
- [ ] Add example queries
- [ ] Include troubleshooting

### Technical Documentation
- [ ] Update API documentation
- [ ] Document database schema
- [ ] Add deployment guide
- [ ] Include maintenance procedures

Create a table at the end of this document with the field id's from the vector database for all the fields.  Provide an example of a value for each field 
Revise the general query responses as per the table above
Revise the specific query responses as per the table above
Debug why the chatbot is not working
Create sub domain dziwani.kwantu.support
Clone only RAG SQL tab onto that URL (we will leave existing demo un changed)
Change 'RAG SQL Chatbot' to 'Welcome to Dwizani!'
Change description to be 'I am Dwizani, a prototype AI chatbot that can answer questions about infrastructure projects.  My name means 'what you should know' in Chichewa.  For now I have access to data on projects being constructed in Malawi'
Make header (see line 7) larger along the lines of example below
Make canvass narrower such that chat area takes up middle of the page
Add following tiles to show the following guidance.  Hide these once the user initiates a chat.

Box one:

Find projects by sector

Ask about health, education or roads.

Box two:

Find project by location

Ask about a specific district or region in Malawi

Box three:

Find a specific project

Ask about a specific project to learn about the contractor and expenditure to date
