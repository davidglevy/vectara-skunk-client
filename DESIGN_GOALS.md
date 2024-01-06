# Design Goals

In making this client for Vectara, I wanted to encapsulate a few key design
goals. Many of these I've brought with me from my prior experience building
enterprise applications.

1. **Don't make me think:** the clients for Vectara services should be intuitive and shield the user from uneccesary
   complexity where possible.
2. **Dependency Injection:** Whilst Python Supports "monkey patching", I strongly prefer using dependency injection. It
   allows us to easily inject common dependency instances (singletons) which mean we can easily reconfigure behaviour
   across our application - for example we can "catch" all requests made with the equivalent of an Aspect.
3. **Stateless:** The invocations from one client call to the next are designed to be stateless. There's a few instances
   where we need state, e.g. "ListAPIKeys" but we defer this to the vectara-skunk-manager.
4. **Strongly Typed:** For users who are first exploring the APIs, parsing proto files is an impedance barrier from
   staying within their environment of choice (e.g. the IDE) and looking at implementation methods. To that end
   the API methods follow two rules:
   1. Strongly Typed: We use Python's Data Classes (see `vectara.domain`) and Enums with the `dacite` library to both:
      1. Validate inputs. In a few cases we allow dicts and these are validated by serializing into a strongly typed
         `dataclass` before being turned back into a dict for our common HTTP request handler.
      2. Validate responses. We deserialize JSON into a dict before turning it into a strongly typed `dataclass`.
   2. Return Objects Must be Declared on methods.
5. **Unit/Integration tests:** We verify all of this functionality with an extensive set of unit/integration tests found
   in the "test" folder.
6. **Convention over Configuration:** If something, say like authentication info, can be stored more easily in a users
   home directory, we'll prefer that over exhaustive configuration. Same for the Factory which wires everything up, it
   should have sensible defaults _however the code should be flexible to allow a different configuration in edge cases_.
7. **Make it Easy:** Ideally if the client is very lightweight and easy to use, we can refactor some of the other
   examples so they can focus on concepts more than REST invocations/response parsing.


## Deviations from Vectara APIs

I've made note where I've made deviations from exposing the raw Vectara APIs and listed the rationale.

### QueryService - query

So far I've found the query API to be very flexible however we can simplify interactions with it with the following
deviations from the raw request/response structures:

1. **Single Query/Response:** From the kinds of application use cases I've seen so far, the most common query operation is a Single query/result.
2. **Singular Corpus Id:** Most queries will be for a single corpus Id Corpus_id can be int or List[int]

I'm also likely to modify some default behavior for edge cases / exceptions:
1. **"No Documents Query Error":** Currently an error is returned when the corpus has no documents in it's corpus but
   honestly this doesn't feel like it should be an exception, it should be "no results" with a status

### AdminService - ListAPIKeys

Okay, I feel like the method right now is designed primarily for allowing a machine client to retrieve
all results, chunking requests to avoid more than say 1000 at a time. The API doesn't really support
user directed pagination as the "pageKey" acts more like an iterator.

To that end:

1. **Retrieve All:** If All clients are just going to be writing their own code to paginate before building their
  own filtering, sorting and pagination, we can at least do the filtering here.
2. **Stateful sorting/pagination in manager:** I'll push up the sorting/pagination into a stateful 
  `vectara-skunk-manager` **(NB: To be built)**

Retrieves all (no pagination, applies filter, no sorting). Reference vectara-skunk-manager

