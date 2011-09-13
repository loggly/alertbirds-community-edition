#Alert Birds (Community Edition)

This is the Community Edition of Alert Birds.  We took out the secrets/apikeys etc that we used so you will want to insert your own for your version of this code to work.  The two locations this information was changed are in /cron.yaml and etc/contrib.py

happy coding!

#Alert Birds
Alert Birds is Loggly's alerting and monitoring app, but just as importantly, it's the reference app for developers. We'll get into what that means for app developers in a little bit, but first, let's cover the basics of what Alert Birds does.

##The Gist
Long story short, Alert Birds runs your Loggly saved searches and notifies you when something's amiss. There are three major components:

Alerts, which will fire from a cron job that runs at an interval you select.
Saved searches, which are stored on Loggly, and get attached to alerts. They're the search query itself, plus the inputs and devices you've chosen to search against.
Endpoints, which is really 'endpoint', because it consists entirely of PagerDuty support for the moment. If an alert fires, you can have Alert Birds trigger an alert in PagerDuty, which then can call or SMS you so that your significant other will be annoyed.
A sample check might be to check whether (ERROR OR WARN) NOT 404 happens more than 10 times in 5 minutes.

If an alert is in a critical state, the cron will check its status every minute instead of the interval you selected, until either the issue goes away, or you disable it and go back to bed.

It is an excellent idea to configure a PagerDuty endpoint, because otherwise, if you don't happen to be on alertbirds.appspot.com (I don't see why that would be the case, because it's pretty snappy) you won't hear the squawks or see the notifications. However, you'll get a gentle reminder when you try to create an alert that's not attached to an endpoint.

##A Couple Important Bits That Should Not Be Glossed Over Spuriously
* One caveat with the real-time notifications (and sounds!) is that Pusher and SoundManager2, the libraries we use respectively, need either Flash or HTML5. It's a good idea to unblock Flash if you can for alertbirds.appspot.com, because HTML5 support in SoundManager2 is still in beta. We default to Flash for that library. Don't worry, no matter how much you dislike Adobe and refuse to support their bugware, you'll still get all of your notifications to PagerDuty.

* iOS devices require user interaction before they will play sounds, so there's really not much for sound support on iPhones and the like. However, you can always go into the alert and click the play button to hear what sound you would have heard.

##Developers, Developers, Developers
As mentioned above, Alert Birds is intended to be the app that developers can use as a reference when developing against Loggly's APIs. To that end, we used as many third-party tools as possible to make it as non-Loggly-centric as possible. 
####A partial list of the tools and technologies we used include:
* Google App Engine
* Google authentication
* OAuth (against loggly.com)
* Tornado
* jQuery
* Pusher
* PagerDuty
* SoundManager2
* WTForms

and it's written in Python and JavaScript. We will be open-sourcing the codebase very shortly on GitHub. In Alert Birds, you'll find useful snippets illustrating a number of common issues, including how you can

authenticate against Loggly using OAuth
run normal and facet searches
create and run saved searches (before we expose them in the Loggly UI!)
trigger and resolve alerts in PagerDuty
retrieve your input and device lists
The basic idea is for us to make it as easy as possible to create the Loggly app you've always dreamed of (like a CLI shell with vim keybindings!) Please share your thoughts on how we can make the app development process easier.

- Hoover J. Beaver, Esq.
