<img src="https://code.freedombone.net/bashrc/epicyon/raw/master/img/logo.png?raw=true" width=256/>

A minimal ActivityPub server.

Based on the specification: https://www.w3.org/TR/activitypub

Also: https://raw.githubusercontent.com/w3c/activitypub/gh-pages/activitypub-tutorial.txt

https://blog.dereferenced.org/what-is-ocap-and-why-should-i-care

https://alexcastano.com/what-is-activity-pub

This project is currently *pre alpha* and not recommended for any real world uses.

## Goals

 * A minimal ActivityPub server, comparable to an email MTA.
 * AGPLv3+
 * Server-to-server and client-to-server protocols supported.
 * Implemented in a common language (Python 3)
 * Keyword filtering.
 * Being able to build crowdsouced organizations with roles and skills
 * Sharings collection, similar to the gnusocial sharings plugin
 * Quotas for received posts per day, per domain and per account
 * Hellthread detection and removal
 * Support content warnings, reporting and blocking.
 * http signatures and basic auth.
 * Compatible with http (onion addresses), https and dat.
 * Minimal dependencies.
 * Capabilities based security
 * Support image blurhashes
 * Data minimization principle. Configurable post expiry time.
 * Likes and repeats only visible to authorized viewers
 * ReplyGuy mitigation - maxmimum replies per post or posts per day
 * Ability to delete or hide specific conversation threads
 * Commandline interface. If there's a GUI it should be a separate project.
 * Designed for intermittent connectivity. Assume network disruptions.
 * Suitable for single board computers.

## Object capabilities workflow

This is one proposed way that OCAP could work.

 * Works from person to person, not instance to instance. Actor-oriented capabilities.
 * Produces negligible additional network traffic, although see the proviso for shared inbox
 * Works in the same way between people on different instances or the same instance
 * People can alter what their followers can do on an individual basis
 * Leverages the existing follow request mechanism

Default capabilities are initially set up when a follow request is made. The Accept activity sent back from a follow request can be received by any instance. A capabilities accept activity is attached to the follow accept.

``` text
                            Alice
                              |
                              V
                        Follow Request
                              |
                              V
                             Bob
                              |
                              V
               Create/store default Capabilities
                          for Alice
                              |
                              V
              Follow Accept + default Capabilities
                              |
                              V
                            Alice
                              |
                              V
                   Store Granted Capabilities
```

The default capabilities could be *any preferred policy* of the instance. They could be no capabilities at all, read only or full access to everything.

Example Follow request from **Alice** to **Bob**:

``` json
{'actor': 'http://alicedomain.net/users/alice',
 'cc': ['https://www.w3.org/ns/activitystreams#Public'],
 'id': 'http://alicedomain.net/users/alice/statuses/1562507338839876',
 'object': 'http://bobdomain.net/users/bob',
 'published': '2019-07-07T13:48:58Z',
 'to': ['http://bobdomain.net/users/bob'],
 'type': 'Follow'}
 ```

Follow Accept from **Bob** to **Alice** with attached capabilities.

``` json
{'actor': 'http://bobdomain.net/users/bob',
 'capabilities': {'actor': 'http://bobdomain.net/users/bob',
                  'capability': ['inbox:write', 'objects:read'],
                  'id': 'http://bobdomain.net/caps/alice@alicedomain.net#rOYtHApyr4ZWDUgEE1KqjhTe0kI3T2wJ',
                  'scope': 'http://alicedomain.net/users/alice',
                  'type': 'Capability'},
 'cc': [],
 'object': {'actor': 'http://alicedomain.net/users/alice',
            'cc': ['https://www.w3.org/ns/activitystreams#Public'],
            'id': 'http://alicedomain.net/users/alice/statuses/1562507338839876',
            'object': 'http://bobdomain.net/users/bob',
            'published': '2019-07-07T13:48:58Z',
            'to': ['http://bobdomain.net/users/bob'],
            'type': 'Follow'},
 'to': ['http://alicedomain.net/users/alice'],
 'type': 'Accept'}
```

When posts are subsequently sent from the following instance (server-to-server) they should have the corresponding capability id string attached within the Create wrapper. To handle the *shared inbox* scenario this should be a list rather than a single string. In the above example that would be *['http://bobdomain.net/caps/alice@alicedomain.net#rOYtHApyr4ZWDUgEE1KqjhTe0kI3T2wJ']*. It should contain a random token which is hard to guess by brute force methods.

NOTE: the token should be random and not a hash of anything. Making it a hash would give an adversary a much better chance of calculating it.

``` text
                            Alice
                              |
                              V
                          Send Post
	     Attach id from Stored Capabilities
	              granted by Bob
                              |
                              V
                             Bob
                              |
                              V
                    http signature check
                              |
                              V
                 Check Capability id matches
                     stored capabilities
                              |
                              V
	       Match stored capability scope
	       against actor on received post
                              |
                              V
                Check that stored capability
		 contains inbox:write, etc
                              |
                              V
                      Any other checks
                              |
                              V
                    Accept incoming post		   
```

Subsequently **Bob** could change the stored capabilities for **Alice** in their database, giving the new object a different id. This could be sent back to **Alice** as an **Update** activity with attached capability.

Bob can send this to Alice, altering *capability* to now include *inbox:noreply*. Notice that the random token at the end of the *id* has changed, so that Alice can't continue to use the old capabilities.

``` json
{'actor': 'http://bobdomain.net/users/bob',
 'cc': [],
 'object': {'actor': 'http://bobdomain.net/users/bob',
            'capability': ['inbox:write', 'objects:read', 'inbox:noreply'],
            'id': 'http://bobdomain.net/caps/alice@alicedomain.net#53nwZhHipNFCNwrJ2sgE8GPx13SnV23X',
            'scope': 'http://alicedomain.net/users/alice',
            'type': 'Capability'},
 'to': ['http://alicedomain.net/users/alice'],
 'type': 'Update'}
```

Alice then receives this and updates her capabilities granted by Bob to:

``` json
{'actor': 'http://bobdomain.net/users/bob',
 'capability': ['inbox:write', 'objects:read', 'inbox:noreply'],
 'id': 'http://bobdomain.net/caps/alice@alicedomain.net#53nwZhHipNFCNwrJ2sgE8GPx13SnV23X',
 'scope': 'http://alicedomain.net/users/alice',
 'type': 'Capability'}
```

If she sets her system to somehow ignore the update then if capabilities are strictly enforced she will no longer be able to send messages to Bob's inbox.

Object capabilities can be strictly enforced by adding the **--ocap** option when running the server. The only activities which it is not enforced upon are **Follow** and **Accept**. Anyone can create a follow request or accept updated capabilities.

## Object capabilities in the shared inbox scenario

Shared inboxes are obviously essential for any kind of scalability, otherwise there would be vast amounts of duplicated messages being dumped onto the intertubes like a big truck.

With the shared inbox instead of sending from Alice to 500 of her fans on a different instance - repeatedly sending the same message to individual inboxes - a single message is sent to its shared inbox (which has its own special account called 'inbox') and it then decides how to distribute that. If a list of capability ids is attached to the message which gets sent to the shared inbox then the receiving server can use that.

When a post arrives in the shared inbox it is checked to see that at least one follower exists for it. If there are only a small number of followers then it is treated like a direct message and copied separately to individual account inboxes after capabilities checks. For larger numbers of followers the capabilities checks are done at the time when the inbox is fetched. This avoids a lot of duplicated storage of posts.

A potential down side is that for popular accounts with many followers the number of capabilities ids (one for each follower on the receiving server) on a post sent to the shared inbox could be large. However, in terms of bandwidth it may still not be very significant compared to heavyweight websites containing a lot of javascript.

## Some capabilities

*inbox:write* - follower can post anything to your inbox

*inbox:noreply* - follower can't reply to your posts

*inbox:nolike* - follower can't like your posts

*inbox:nopics* - follower can't post image links

*inbox:noannounce* - follower can't send repeats (announce activities) to your inbox

*inbox:cw* - follower can't post to your inbox unless they include a content warning

## Object capabilities adversaries

If **Eve** subsequently learns what the capabilities id is for **Alice** by somehow intercepting the traffic (eg. suppose she works for *Eveflare*) then she can't gain the capabilities of Alice due to the *scope* parameter against which the actors of incoming posts are checked.

**Eve** could create a post pretending to be from Alice's domain, but the http signature check would fail due to her not having Alice's keys.

The only scenarios in which Eve might triumph would be if she could also do DNS highjacking and:

 * Bob isn't storing Alice's public key and looks it up repeatedly
 * Alice and Bob's instances are foolishly configured to perform *blind key rotation* such that her being in the middle is indistinguishable from expected key changes

Even if Eve has an account on Alice's instance this won't help her very much unless she can get write access to the database.

Another scenario is that you grant capabilities to an account on a hostile instance. The hostile instance then shares the resulting token with all other accounts on it. Potentially those other accounts might be able to gain capabilities which they havn't been granted *but only if they also have identical signing keys*. Checking for public key duplication on the instance granting capabilities could mitigate this. At the point at which a capabilities request is made are there any other known accounts with the same public key? Since actors are public it would also be possible to automatically scan for the existence of instances with duplicated signing keys.

## Install

On Arch/Parabola:

``` bash
sudo pacman -S tor python-pip python-pysocks python-pycryptodome python-beautifulsoup4 imagemagick python-pillow python-numpy
sudo pip install commentjson
```

Or on Debian:

``` bash
sudo apt-get -y install tor python3-pip python3-socks imagemagick python3-numpy python3-setuptools python3-crypto python3-pil.imagetk
sudo pip3 install commentjson beautifulsoup4 pycryptodome
```

## Running Tests

To run the unit tests:

``` bash
python3 epicyon.py --tests
```

To run the network tests. These simulate instances exchanging messages.

``` bash
python3 epicyon.py --testsnetwork
```

## Viewing Public Posts

To view the public posts for a person:

``` bash
python3 epicyon.py --posts nickname@domain
```

If you want to view the raw json:

``` bash
python3 epicyon.py --postsraw nickname@domain
```

## Account Management

To add a new account:

``` bash
python3 epicyon.py --addaccount nickname@domain --password [yourpassword]
```

To remove an account (be careful!):

``` bash
python3 epicyon.py --rmaccount nickname@domain
```

To change the password for an account:

``` bash
python3 epicyon.py --changepassword nickname@domain newpassword
```

To set an avatar for an account:

``` bash
python3 epicyon.py --nickname [nick] --domain [name] --avatar [image filename]
```

To set the background image for an account:

``` bash
python3 epicyon.py --nickname [nick] --domain [name] --background [image filename]
```

## Running the Server

To run with defaults:

``` bash
python3 epicyon.py
```

In a browser of choice (but not Tor browser) you can then navigate to:

``` text
http://localhost:8085/users/admin
```

If it's working then you should see the json actor for the default admin account.

For a more realistic installation you can run on a defined domain and port:

``` bash
python3 epicyon.py --domain [name] --port 8000 --https
```

You will need to proxy port 8000 through your web server and set up CA certificates as needed.

By default data will be stored in the directory in which you run the server, but you can also specify a directory:

``` bash
python3 epicyon.py --domain [name] --port 8000 --https --path [data directory]
```

By default the server will federate with any others. You can limit this to a well-defined list with the *--federate* option.

``` bash
python3 epicyon.py --domain [name] --port 8000 --https --federate domain1.net domain2.org domain3.co.uk
```

## Following other accounts

With your server running you can then follow other accounts with:

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] --follow othernick@domain --password [c2s password]
```

The password is for the client to obtain access to the server.

You may or may not need to use the *--port*, *--https* and *--tor* options, depending upon how your server was set up.

Unfollowing is silimar:

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] --unfollow othernick@domain --password [c2s password]
```

## Sending posts

To make a public post:

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] \
                   --sendto public --message "hello" \
		   --warning "This is a content warning" \
		   --password [c2s password]
```

To post to followers only:

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] \
                   --sendto followers --message "hello" \
		   --warning "This is a content warning" \
		   --password [c2s password]
```

To send a post to a particular address (direct message):

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] \
                   --sendto othernick@domain --message "hello" \
		   --warning "This is a content warning" \
		   --password [c2s password]
```

The password is the c2s password for your account.

You can also attach an image. It must be in png, jpg or gif format.

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] \
                   --sendto othernick@domain --message "bees!" \
		   --warning "bee-related content" --attach bees.png \
		   --imagedescription "bees on flowers" \
		   --blurhash \
		   --password [c2s password]
```

## Delete posts

To delete a post which you wrote you must first know its url. It is usually something like:

``` text
https://yourDomain/users/yourNickname/statuses/number
```

Once you know that they you can use the command:

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] \
                   --delete [url] --password [c2s password]
```

Deletion of posts in a federated system is not always reliable. Some instances may not implement deletion, and this may be because of the possibility of spurious deletes being sent by an adversary to cause trouble.

By default federated deletions are not permitted because of the potential for misuse. If you wish to enable it then set the option **--allowdeletion**.

Another complication of federated deletion is that the followers collection may change between the time when a post was created and the time it was deleted, leaving some stranded copies.

## Announcements/repeats/boosts

To announce or repeat a post you will first need to know it's url. It is usually something like:

``` text
https://domain/users/name/statuses/number
```

Once you know that they you can use the command:

``` bash
python3 epicyon.py --nickname [yournick] --domain [name] \
                   --repeat [url] --password [c2s password]
```

## Archiving posts

You can archive old posts with:

``` bash
python3 epicyon.py --archive [directory]
```

Which will move old posts to the given directory. You can also specify the number of weeks after which images will be archived, and the maximum number of posts within in/outboxes.

``` bash
python3 epicyon.py --archive [directory] --archiveweeks 4 --maxposts 256
```

If you want old posts to be deleted for data minimization purposes then the archive location can be set to */dev/null*.

``` bash
python3 epicyon.py --archive /dev/null --archiveweeks 4 --maxposts 256
```

## Roles and skills

To build crowdsourced organizations you might want to assign roles and skills to individuals. This can be done with some command options:

To assign a role to someone:

``` bash
python3 epicyon.py --nickname susan --domain somedomain.net --project "instance" --role "moderator"
```

Individuals can be assigned to multiple roles within multiple projects if needed.

You might also want to advertize that you have various skills. Skill levels are a percentage value.

``` bash
python3 epicyon.py --nickname jon --domain somedomain.net --skill "Dressmaking" --level 60
```

You can also set a busy status to define whether people are available for new tasks.

``` bash
python3 epicyon.py --nickname eva --domain somedomain.net --availability ready
```

With roles, skills and availability defined tasks may then be automatically assigned to the relevant people, or load balanced as volunteers come and go and complete pieces of work. Orgbots may collect that information and rapidly assemble a viable organization from predefined schemas. This is the way to produce effective non-hierarchical organizations which are also transient with no fixed bureaucracy.

## Blocking and unblocking

Whether you are using the **--federate** option to define a set of allowed instances or not, you may want to block particular accounts even inside of the perimeter. To block an account:

``` bash
python3 epicyon.py --nickname yournick --domain yourdomain --block somenick@somedomain
```

This blocks at the earliest possble stage of receiving messages, such that nothing from the specified account will be written to your inbox.

Or to unblock:

``` bash
python3 epicyon.py --nickname yournick --domain yourdomain --unblock somenick@somedomain
```

## Filtering on words or phrases

Blocking based upon the content of a message containing certain words or phrases is relatively crude and not always effective, but can help to reduce unwanted communications.

To add a word or phrase to be filtered out:

``` bash
python3 epicyon.py --nickname yournick --domain yourdomain --filter "this is a filtered phrase"
```

It can also be removed with:

``` bash
python3 epicyon.py --nickname yournick --domain yourdomain --unfilter "this is a filtered phrase"
```

Like blocking, filters are per account and so different accounts on a server can have differing filter policies.

You can also combine words or phrases with "+", such that they can be present in different parts of the message:

``` bash
python3 epicyon.py --nickname yournick --domain yourdomain --filter "blockedword+some other phrase"
```

## Applying quotas

A common adversarial situation is that a hostile server tries to flood your shared inbox with posts in order to try to overload your system. To mitigate this it's possible to add quotas for the maximum number of received messages per domain per day and per account per day.

If you're running the server it would look like this:

``` bash
python3 epicyon.py --domainmax 1000 --accountmax 200
```

With these settings you're going to be receiving no more than 200 messages for any given account within a day.
