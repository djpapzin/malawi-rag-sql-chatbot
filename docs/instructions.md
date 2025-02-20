# Development Guidelines

1. **Query Processing (Current Rule-Based System)**
- Implement separate handlers for general/specific queries
- Use regex patterns for query classification
- Log all query classification decisions
- Validate query results against both API and database
- Handle edge cases for construction project queries
- Implement proper error handling for all query types
- Support case-insensitive project code matching
- Implement fuzzy matching for project names
- Handle quoted and unquoted project names
- Support multiple query formats for the same intent
- Document all regex patterns
- Test pattern matching thoroughly

2. **Response Generation**
- Follow standardized JSON response format
- Include metadata with all responses
- Properly format currency and date values
- Handle null/missing values consistently
- Include comprehensive error messages
- Maintain response size limits
- Ensure field availability tracking
- Implement response templates by query type
- Add source attribution for results
- Document template structure

3. **Pattern Matching Rules**
- Maintain clear regex documentation
- Keep patterns simple and maintainable
- Test patterns with edge cases
- Handle case sensitivity appropriately
- Support partial matches where needed
- Document pattern limitations
- Regular pattern review and optimization
- Track pattern performance
- Handle special characters
- Support multiple languages

4. **Field Handling**
- Always reference fields by mapped IDs
- Validate field existence during initialization
- Maintain field metadata registry
- Handle field type conversions properly
- Validate data consistency across sources
- Implement field value formatting
- Track required vs optional fields
- Handle field dependencies
- Support field aliases
- Validate field value ranges

5. **UI Development**
- Keep guidance messages configurable
- Implement feature toggles for new components
- Maintain responsive design principles
- Provide clear error feedback
- Support multiple query input methods
- Handle long-running queries appropriately
- Implement dynamic result display
- Add progress indicators
- Support result pagination
- Implement sorting and filtering

6. **Testing**
- Validate against all documented test cases
- Monitor query success/failure rates
- Perform regular data freshness checks
- Test with real API responses
- Validate response formats
- Check error handling scenarios
- Test edge cases systematically
- Verify field availability
- Compare API and DB results
- Track performance metrics
- Test pattern matching extensively

7. **Documentation**
- Keep API response examples up to date
- Document all regex patterns
- Document all error scenarios
- Maintain clear troubleshooting guides
- Update field mappings regularly
- Document performance considerations
- Include test case descriptions
- Document query patterns
- Maintain version history
- Track known limitations
- Include deployment guides

8. **Performance Monitoring**
- Track query response times
- Monitor pattern matching performance
- Log database query performance
- Track memory usage
- Monitor API availability
- Track error rates
- Monitor resource utilization
- Implement performance alerts
- Track cache effectiveness
- Monitor concurrent requests

9. **Security**
- Validate input parameters
- Implement rate limiting
- Handle sensitive data appropriately
- Monitor access patterns
- Implement error masking
- Validate API tokens
- Monitor authentication
- Track security events
- Handle data privacy
- Implement access controls

10. **Planned LLM Integration**
- Prepare for LLM integration
- Design LLM prompt templates
- Plan confidence scoring system
- Design fallback mechanisms
- Consider response generation approach
- Plan context management
- Design multi-turn conversation flow
- Consider performance implications
- Plan testing strategy
- Document integration requirements
