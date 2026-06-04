## ADDED Requirements

### Requirement: Follow HTTP redirects when fetching feeds

The system SHALL follow HTTP redirects (301, 302, 307, 308) when making requests to fetch RSS feed content.

#### Scenario: Feed URL redirects to HTTPS
- **WHEN** a feed URL returns a 301 redirect to an HTTPS URL
- **THEN** the system SHALL follow the redirect
- **AND** fetch and parse the feed content from the final URL

#### Scenario: Feed URL with multiple redirects
- **WHEN** a feed URL returns multiple consecutive redirects
- **THEN** the system SHALL follow all redirects
- **AND** fetch and parse the feed content from the final URL
