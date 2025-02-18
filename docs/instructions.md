# Development Guidelines

1. **Field Handling**
- Always reference fields by mapped IDs
- Validate field existence during initialization
- Maintain field metadata registry

2. **Query Processing**
- Implement separate handlers for general/specific
- Use confidence thresholds for query typing
- Log all query classification decisions

3. **UI Development**
- Keep guidance messages configurable
- Implement feature toggles for new components
- Maintain responsive design principles

4. **Testing**
- Validate against all documented test cases
- Monitor query success/failure rates
- Perform regular data freshness checks
