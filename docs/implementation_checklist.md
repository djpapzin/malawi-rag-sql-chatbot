# Implementation Checklist

## Phase 1: Simplify Classification
- [x] Update QueryType enum in `app/llm_classification/classifier.py`
- [x] Modify QueryParameters class in `app/llm_classification/classifier.py`
- [x] Create new classifier implementation in `app/llm_classification/new_classifier.py`
- [ ] Update imports and dependencies
- [ ] Test basic classification structure
- [ ] Migrate existing code to use new classifier

## Phase 2: Enhance LLM Classification
- [x] Update LLM prompt to focus on three main categories
- [x] Implement conversation history tracking
- [x] Add context handling for follow-up questions
- [ ] Test LLM classification with sample queries
- [ ] Fine-tune prompt based on test results

## Phase 3: Simplify Query Building
- [ ] Create separate query builders in `app/query_parser.py`
- [ ] Remove regex-based classification
- [ ] Update SQL query generation
- [ ] Test query building with various scenarios
- [ ] Add error handling for invalid queries

## Phase 4: Testing and Refinement
- [ ] Create test cases for each query type
- [ ] Test edge cases and combinations
- [ ] Gather feedback on response quality
- [ ] Fine-tune LLM prompts and parameters
- [ ] Document new classification system

## Current Status
- Completed Phase 1 core changes
- Created new classifier implementation
- Next: Update imports and dependencies, then begin testing 