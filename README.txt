WHAT IS THIS?
-------------
A Django app to retrieve posts from a Tumblr account, save them to DB as a cache and show them in a simple blog style (listing + single post views). The admin side supports right now settings for the Tumblr account plus setting the visibility of tags and posts (so you can hide some of the posts).

I have developed this app based on my own needs but hopefully it will be useful for someone else. It has been tested under Django 1.3. Basic unit tests and case are included.


LICENCE
-------
Copyright (c) 2012, Angel Justo, AJweb.eu

Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE OFFICERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.


TODO
----
* Admin: settings for tumblr account + reading settings
* Support multiple tumblr accounts
* Pages for: monthly, yearly, tag, type
* Search
