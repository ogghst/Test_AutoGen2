# User Stories Gathering Agent

A specialized AI agent that unpacks high-level requirements into comprehensive user stories with EARS (Easy Approach to Requirements Syntax) notation acceptance criteria.

## 🎯 Purpose

The User Stories Gathering Agent transforms vague requirements like "Add a review system for products" into detailed, actionable user stories that cover:

- **Viewing reviews** - Display, pagination, sorting
- **Creating reviews** - Input validation, authentication, content moderation
- **Filtering reviews** - Search, filtering, advanced queries
- **Rating reviews** - Helpfulness voting, fraud prevention
- **Review moderation** - Content quality, community standards
- **Analytics** - Business insights, performance metrics

## 🏗️ Architecture

The agent integrates seamlessly with the existing multi-agent system:

```
User Request → Triage Agent → User Stories Agent → Comprehensive User Stories
```

### Key Components

- **UserStoriesAgent**: Main agent class extending `AIAgent`
- **EARS Notation Tools**: Generate acceptance criteria in standard format
- **Review System Templates**: Pre-built comprehensive story sets
- **Edge Case Coverage**: Handles scenarios developers typically encounter

## 🚀 Quick Start

### 1. Basic Usage

```python
from project_management_system.agents.user_stories_agent import UserStoriesAgent

# Create agent
agent = UserStoriesAgent(model_client)

# Generate comprehensive review system stories
stories = await agent._delegate_tools["create_review_system_stories"].run_json(
    {"system_name": "Product Review System"},
    None
)
```

### 2. Individual User Story Generation

```python
# Generate single user story
story = await agent._delegate_tools["generate_user_story"].run_json(
    {
        "title": "View Product Reviews",
        "user_role": "customer",
        "requirement": "view product reviews to make informed decisions",
        "acceptance_criteria_count": 8
    },
    None
)
```

### 3. EARS Criteria Generation

```python
# Generate EARS notation criteria
criteria = await agent._delegate_tools["generate_ears_criteria"].run_json(
    {
        "requirement": "User authentication for review creation",
        "criteria_type": "all"
    },
    None
)
```

## 📋 EARS Notation

The agent generates acceptance criteria using the **Easy Approach to Requirements Syntax**:

### Ubiquitous Requirements (Always True)
- The system shall always validate user input before processing
- The system shall always maintain data integrity and consistency

### Event-Driven Requirements (When X Happens)
- When the user submits a review, the system shall save it within 2 seconds
- When validation fails, the system shall display specific error messages

### State-Driven Requirements (While X is True)
- While the user is authenticated, the system shall maintain their session
- While processing, the system shall show a loading indicator

### Unwanted Behavior Requirements (Never X)
- The system shall never expose sensitive user data
- The system shall never allow unauthorized access

## 🔧 Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `create_review_system_stories` | Generate complete review system stories | `system_name` |
| `generate_user_story` | Create individual user story | `title`, `user_role`, `requirement`, `acceptance_criteria_count` |
| `generate_ears_criteria` | Generate EARS notation criteria | `requirement`, `criteria_type` |

## 📚 Example Output

### Sample User Story: View Product Reviews

```markdown
# User Story: View Product Reviews

**As a** customer  
**I want** to view product reviews  
**So that** I can make informed purchasing decisions

## Acceptance Criteria (EARS Notation)

### Ubiquitous Requirements (Always True)
- The system shall always display reviews in a readable, accessible format
- The system shall always show review metadata (date, rating, helpful votes)

### Event-Driven Requirements (When X Happens)
- When a user requests reviews, the system shall load them within 3 seconds
- When no reviews exist, the system shall display an appropriate "no reviews" message

### State-Driven Requirements (While X is True)
- While loading reviews, the system shall show a loading indicator
- While displaying reviews, the system shall maintain scroll position

### Unwanted Behavior Requirements (Never X)
- The system shall never display incomplete or corrupted review data
- The system shall never expose private user information in reviews

#### Edge Cases & Developer Considerations
- Handle large numbers of reviews (pagination, virtual scrolling)
- Implement caching for frequently accessed reviews
- Consider mobile vs desktop display differences
- Plan for internationalization (different date formats, languages)
```

## 🧪 Testing

Run the test script to see the agent in action:

```bash
python test_user_stories_agent.py
```

This will:
1. Test individual tool functions
2. Generate comprehensive review system stories
3. Verify agent integration with the factory
4. Save outputs to `output_documents/` folder

## 🔍 Edge Cases Covered

The agent addresses scenarios developers typically handle:

### Performance & Scalability
- Large dataset handling (pagination, virtual scrolling)
- Caching strategies and optimization
- Rate limiting and abuse prevention
- Network timeout and retry logic

### Security & Validation
- Input sanitization and validation
- Authentication and authorization
- CSRF protection and security headers
- Content filtering and moderation

### User Experience
- Loading states and progress indicators
- Error handling and recovery
- Accessibility compliance (WCAG 2.1 AA)
- Internationalization support

### Data Integrity
- Concurrent access handling
- Transaction management
- Data consistency and validation
- Audit trails and logging

## 🚀 Integration

### With Triage Agent

The triage agent automatically routes user story requests:

```
User: "Generate user stories for a review system"
Triage Agent → Routes to User Stories Agent
User Stories Agent → Generates comprehensive stories
```

### With Existing System

The agent follows the established patterns:
- Extends `AIAgent` base class
- Uses standard tool execution framework
- Integrates with message routing system
- Follows AutoGen API specifications

## 📁 File Structure

```
project_management_system/
├── agents/
│   ├── user_stories_agent.py          # Main agent implementation
│   ├── tools.py                       # Tool functions and constants
│   ├── factory.py                     # Agent registration
│   └── triage_agent.py               # Routing logic
├── base/
│   └── AIAgent.py                     # Base agent class
└── models/
    └── data_models.py                 # Data structures
```

## 🎯 Use Cases

### 1. Requirements Gathering
Transform high-level requirements into detailed, testable user stories

### 2. Development Planning
Provide developers with comprehensive acceptance criteria and edge cases

### 3. Quality Assurance
Ensure all scenarios are covered in testing and validation

### 4. Stakeholder Communication
Present requirements in clear, understandable format for business users

### 5. Agile Development
Support sprint planning with well-defined user stories and acceptance criteria

## 🔧 Configuration

The agent uses the standard configuration system:

```python
# Environment variables
OPENAI_API_KEY=your_api_key
MODEL_PROVIDER=openai  # or mock, ollama, etc.
MODEL_NAME=gpt-4

# Configuration file
config.json
```

## 📈 Future Enhancements

Potential improvements for the agent:

- **Template Library**: Pre-built story templates for common systems
- **Custom EARS Patterns**: User-defined acceptance criteria patterns
- **Story Validation**: Automated validation of story completeness
- **Integration APIs**: Connect with project management tools
- **Multi-language Support**: Generate stories in different languages

## 🤝 Contributing

To extend the agent:

1. **Add New Tools**: Implement functions in `tools.py`
2. **Extend EARS Patterns**: Add new criteria types
3. **Create Templates**: Build story templates for specific domains
4. **Improve Edge Cases**: Add more developer scenarios

## 📚 Resources

- [EARS Notation Guide](https://www.requirements.com/ears-notation)
- [AutoGen Framework](https://microsoft.github.io/autogen/)
- [User Story Best Practices](https://www.agilealliance.org/glossary/user-stories/)
- [Acceptance Criteria Examples](https://www.atlassian.com/agile/project-management/user-stories)

## 📄 License

This project follows the same license as the main project management system.

---

**Ready to transform your requirements into comprehensive user stories?** 

The User Stories Gathering Agent is your AI-powered partner for creating detailed, actionable user stories with professional-grade acceptance criteria that cover all the edge cases developers need to handle.
