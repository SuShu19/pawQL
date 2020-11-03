

first_pr_page = """{
  repository(owner: "%s", name: "%s") {
    owner{
        login
      }
    name
    %s(first:100){
      totalCount
      pageInfo{
        hasNextPage
        hasPreviousPage
      }
      edges{
        cursor
      }
      nodes{
        number
        url
        createdAt
        title
        body
        comments(first:100){
          nodes{
            author{login}
            body
            createdAt
            url
          }
          totalCount
        }
        reviews(first:50){
          nodes{
            author{login}
            body
            comments(first:50){
              nodes{
                author{login}
                createdAt
                body
              }              
            }
          }
        }
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          totalCount
        }
      }
    }
  }
}
"""

other_pr_page = """{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(first:100,after:"%s"){
      totalCount
      pageInfo{
        hasNextPage
        hasPreviousPage
      }
      edges{
        cursor
      }
      nodes{
        number
        url
        createdAt
        title
        body
        comments(first:100){
          nodes{
            author{login}
            body
            createdAt
            url
          }
          totalCount
        }
        reviews(first:50){
          nodes{
            author{login}
            body
            comments(first:50){
              nodes{
                author{login}
                createdAt
                body
              }              
            }
          }
        }
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          totalCount
        }
      }
    }
  }
}
"""

first_iss_page = """{
  repository(owner: "%s", name: "%s") {
    owner{
        login
      }
    name
    %s(first:100){
      totalCount
      pageInfo{
        hasNextPage
        hasPreviousPage
      }
      edges{
        cursor
      }
      nodes{
        number
        url
        createdAt
        title
        body
        comments(first:100){
          nodes{
            author{login}
            body
            createdAt
            url
          }
          totalCount
        }
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          totalCount
        }
      }
    }
  }
}
"""

other_iss_page = """{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(first:100,after:"%s"){
      totalCount
      pageInfo{
        hasNextPage
        hasPreviousPage
      }
      edges{
        cursor
      }
      nodes{
        number
        url
        createdAt
        title
        body
        comments(first:100){
          nodes{
            author{login}
            body
            createdAt
            url
          }
          totalCount
        }
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          totalCount
        }
      }
    }
  }
}
"""