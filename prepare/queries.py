# pr page 比 issue page 多 reviews

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
        author{login}
        number
        url
        createdAt
        title
        body
        comments(first:100%s){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
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
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
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
        author{login}
        number
        url
        createdAt
        title
        body
        comments(first:100%s){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
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
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
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
        author{login}
        number
        url
        createdAt
        title
        body
        comments(first:100%s){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
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
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
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
        author{login}
        number
        url
        createdAt
        title
        body
        comments(first:100%s){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
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
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
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







































search_100_nodes = """{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(first:80%s){
      totalCount
      pageInfo{
        hasNextPage
        hasPreviousPage
      }
      edges{
        cursor
      }
      nodes{
        author{login}
        number
        url
        createdAt
        title
        body
        comments(first:100){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
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
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                  id 
                }
              }
              target {
                ... on Issue{
                  repository{
                    owner{login}
                    name
                  }
                  number 
                  url
                  title
                  createdAt
                }
                ... on PullRequest{
                  repository{
                    owner{login}
                    name
                  }
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
          edges{
            cursor
          }
          totalCount
        }
      }
    }
  }
}
"""


search_one_node = """
{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(number:%s){
      author{login}
      number
      url
      createdAt
      title
      body
      comments(first:100){
        pageInfo{
          hasNextPage
        }
        edges{
          cursor
        }
        nodes{
          author{login}
          body
          createdAt
          url
        }
        totalCount
      }
    }
  }
}
"""

sear_morethan_100_comments = """{
  repository(owner: "%s", name: "%s") {
    owner{
      login
    }
    name
    %s(number:%s){
      author{login}
      number
      url
      createdAt
      title
      body
      comments(first:100%s){
        pageInfo{
          hasNextPage
        }
        edges{
          cursor
        }
        nodes{
          author{login}
          body
          createdAt
          url
        }
        totalCount
      }
    }
  }
}
"""

sear_morethan_100_timelineItems = """{
  repository(owner: "%s", name: "%s") {
    owner{
        login
      }
    name
    %s(number:%s){
        author{login}
        number
        url
        createdAt
        title
        body
        timelineItems(first:100%s){
          pageInfo{
            hasNextPage
          }
          edges{
            cursor
          }
          totalCount
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
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
              }
              ... on PullRequest{
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
                id 
              }
            }
            target {
              ... on Issue{
                repository{
                  owner{login}
                  name
                }
                number 
                url
                title
                createdAt
              }
              ... on PullRequest{
                repository{
                  owner{login}
                  name
                }
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
      }
    }
  }
}
"""