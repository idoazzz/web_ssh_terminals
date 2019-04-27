Runner web shells is an elegant way setup a centralized testing server. This testing server will run tests for multiple users simultaneously from a given repo/directory (configurable) and exposes the users an interactive web shells that can use for debugging and investegating bugs or state checking in realtime. <br>
Another classic use is if you want run tests/programs with another users (All can have the same web shell).

<br>
Runner web shell is an interactive web shell that controls an interactive process (runner). <br>
The control action is using the STDIN. <br>
The Web Shell getting the STDOUT in real time and shows it on the browser terminal. <br>
<br>
It possible to run several runners on the server and get multiple web interactive shells for each run.
<br>

Runner is a process that has a job and can be interactive with
user commander. User can insert input interactively to the process and
also read the output of the process, interactively. <br>
For example, Shell can be a runner, it's an infinite process that can
getting input and return output while it's running.

More optional uses:  <br>
* Runner web shell offers you a way of sharing program running state. 
* Runner web shell can be used as a Web Shell (The runner that will be runned is /bin/bash).
* Runner web shell can run the target process in a remote computer (The server connects to the remote computer).
<br>
