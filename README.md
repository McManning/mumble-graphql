## Usage

## API

Note that there is no authentication implemented for the GraphQL API. Do not expose to it to the public.

### Queries

```graphql
query GetServers {
  servers {
    id
    isRunning

    # All connected users
    users {
      ...UserFragment
    }

    # All channels as a flat list
    channels {
      ...ChannelFragment
    }
  }
}

fragment ChannelFragment on Channel {
  id
  name
  parent
  links
  description
  temporary
  position
}

fragment UserFragment on User {
  id
  userId
  name
  comment
  channel
  mute
  selfMute
  deaf
  selfDeaf
  suppress
  recording

  # Connection info
  onlineSecs
  idleSecs
  bytesPerSec

  # Client info
  os
  osVersion
  version
  release
}
```

### Mutations

```graphql
mutation UpdateWelcomeMessage {
  updateWelcomeMessage(serverId: "1", text: "Welcome to my server!")
}

mutation SendMessageToChannel {
  sendChannelMessage(
    serverId: "1"
    channelId: "3"
    text: "Hey guys!"
    tree: false
  )
}

mutation SuppressUser {
  userState(
    serverId: "1"
    input: {
      id: "2" # Session ID of the user, not registered ID
      suppress: false
    }
  )
}
```

### Subscriptions

Subscriptions are against all servers simultaneously. Subscriptions will stay connected even if a Mumble server is stopped or restarted.

```graphql
# User sends a message to one or more channels or directly to other users
subscription TextMessage {
  textMessage {
    text
    serverId
    userId
    channelIds
    sessionIds
  }
}

# User (dis)connects, changes channel, changes muted/deafened state,
# starts/stops recording, changes comment, etc.
# State timers (idleSecs, onlineSecs) are not considered.
subscription UserChange {
  userChange {
    changeType # CONNECTED, DISCONNECTED, STATE_CHANGED
    serverId
    user {
      ...UserFragment
    }
  }
}
```
