# LLM-Driven Implementation Plan: Minimizing Hard-Coding in Dziwani Chatbot

## Overview

This plan outlines the strategy for reducing hard-coded elements in the Malawi infrastructure projects chatbot by leveraging LLM capabilities more effectively. The goal is to create a more flexible, maintainable system that can adapt to changing requirements with minimal code changes.

## Phase 1: Assessment (1-2 days)

### Current Hard-Coded Elements Checklist
- [x] **Prompt Templates**: Identify all hard-coded prompt templates
  - Current implementation uses fixed prompts in `langchain_sql.py` for SQL generation and intent detection
  - Together AI with Meta-Llama-3.1-8B-Instruct-Turbo-128K model is used with fixed temperature
- [x] **Response Structures**: Map out fixed response formats and field orderings
  - `ResponseGenerator` class uses hard-coded field orders (`general_field_order`, `specific_field_order`)
  - Fixed formatting for currency, dates, and percentages
- [x] **Intent Detection Patterns**: Document current intent detection logic
  - Basic intent detection using regex patterns and keyword matching
  - Limited to GREETING, GENERAL, SQL, OTHER categories
- [x] **SQL Generation Rules**: Identify limitations in current SQL generation
  - SQL extraction using regex patterns from LLM responses
  - No dynamic schema understanding or query validation
- [x] **Formatting Logic**: List all hard-coded formatting rules
  - Currency formatting fixed to "MWK {value:,.2f}"
  - Date formatting and percentage handling is hard-coded
- [x] **Error Handling**: Document fixed error messages and recovery paths
  - Basic error handling with limited context-aware recovery

### Current LangChain Integration Points
- [x] **SQL Database Connection**: Using SQLite database through custom DatabaseManager
- [x] **LLM Integration**: Using Together AI API directly rather than LangChain's abstractions
- [x] **Query Execution**: Custom implementation for executing SQL queries
- [x] **Response Processing**: Custom response formatting rather than LangChain's output parsers

## Phase 2: Architecture Design (2-3 days)

### Core Components Checklist
- [ ] **LLMResponseManager**: Design centralized LLM interaction component
  - [x] Basic structure created in `llm_response_manager.py`
  - [ ] Integration with existing LangChain components
  - [ ] Adaptation to current project structure
- [ ] **Dynamic Prompt Generation**: Design approach for context-aware prompts
  - [ ] Schema-aware prompt generation
  - [ ] Intent-based prompt selection
- [ ] **Intent Analysis**: Design enhanced intent understanding system
  - [ ] Entity extraction for Malawi-specific locations
  - [ ] Project type classification
  - [ ] Query complexity analysis
- [ ] **Adaptive Response Generation**: Create flexible response framework
  - [x] Basic response handler created in `response_handler.py`
  - [ ] Integration with existing response generator
  - [ ] Dynamic field selection based on query context
- [ ] **Error Recovery**: Design more intelligent error handling
  - [ ] Query validation and correction
  - [ ] Fallback mechanisms for failed queries

### Architecture Deliverables
- [ ] Architecture diagram showing component interactions
- [ ] Interface definitions for key components
- [ ] Prompt engineering guidelines
- [ ] Performance optimization strategy (caching, etc.)
- [x] LangChain integration strategy

## Phase 3: Core Implementation (5-7 days)

### Implementation Checklist

#### Foundation Components
- [x] Create `LLMResponseManager` class (basic implementation)
- [ ] Implement prompt template management
- [ ] Add LLM response validation and error handling
- [ ] Build caching mechanism for LLM responses
- [ ] Integrate with existing LangChain SQL components

#### Enhanced Intent Understanding
- [ ] Implement `understand_query_intent` method
- [ ] Create fallback mechanisms for intent detection failures
- [ ] Add context tracking for multi-turn conversations
- [ ] Test with diverse query patterns
- [ ] Add Malawi-specific entity recognition (districts, project types)

#### Dynamic Response Generation
- [x] Create basic `ResponseHandler` class
- [ ] Implement `generate_dynamic_response` method
- [ ] Create response formatting pipeline
- [ ] Add support for various response types
- [ ] Implement context-aware formatting

#### Adaptive SQL Generation
- [ ] Enhance SQL generation with schema understanding
- [ ] Add query validation and sanitization
- [ ] Implement query optimization suggestions
- [ ] Create SQL explanation capability
- [ ] Add support for complex joins and aggregations

## Phase 4: Integration (3-4 days)

### Integration Checklist
- [ ] Update `process_query` method to use new components
- [ ] Modify response handling in API endpoints
- [ ] Refactor existing hard-coded elements
- [ ] Create smooth transition path between old and new approaches
- [ ] Implement feature flags for gradual rollout
- [ ] Ensure compatibility with existing LangChain components

## Phase 5: Testing & Validation (3-5 days)

### Testing Checklist
- [ ] Create test suite for LLM response generation
- [ ] Test with diverse query patterns
- [ ] Validate SQL generation safety
- [ ] Benchmark performance against baseline
- [ ] Test recovery paths and fallback mechanisms
- [ ] Conduct mock user conversations
- [ ] Compare results between current and new approaches

### Validation Metrics
- [ ] Response quality assessment
- [ ] Intent detection accuracy
- [ ] SQL generation correctness
- [ ] Response time benchmarks
- [ ] Error rate tracking

## Phase 6: Deployment & Monitoring (2-3 days)

### Deployment Checklist
- [ ] Deploy to staging environment (http://154.0.164.254:5000)
- [ ] Configure monitoring for LLM usage
- [ ] Set up alerting for critical failures
- [ ] Create dashboard for key metrics
- [ ] Document new components and usage patterns

### Ongoing Monitoring
- [ ] Track LLM token usage
- [ ] Monitor response quality
- [ ] Analyze failed queries
- [ ] Gather user feedback
- [ ] Regular prompt engineering reviews

## Implementation Timeline

| Phase | Duration | Key Milestones |
|-------|----------|----------------|
| Assessment | 1-2 days | Complete inventory of hard-coded elements |
| Architecture | 2-3 days | Finalized component design |
| Implementation | 5-7 days | Core components functional |
| Integration | 3-4 days | End-to-end flow working |
| Testing | 3-5 days | Quality metrics meeting targets |
| Deployment | 2-3 days | System live with monitoring |

**Total Estimated Time**: 16-24 days

## Success Criteria

- 80% reduction in hard-coded prompt templates
- Successful handling of 95% of test queries
- Response generation time under 3 seconds
- Ability to adapt to schema changes without code modifications
- Improved response quality based on user feedback

## Risk Management

| Risk | Mitigation |
|------|------------|
| LLM response inconsistency | Implement validation and fallbacks |
| Performance degradation | Add caching and optimization |
| High token usage costs | Monitor and optimize prompt length |
| Schema changes breaking queries | Add schema validation checks |
| Complex queries failing | Implement targeted fallback approaches |

## Next Steps

1. Complete the assessment phase inventory
2. Schedule architecture review meeting
3. Create detailed task breakdown for implementation
4. Set up development environment with required dependencies
5. Begin implementing foundation components
