Dinning Cryptographers Problem
==================================
##### Authors:
Michał Gadowicz & Malinowski Kamil

----------------------------------
### 1. Scope

#### 1.1 Problem statement

The Dining Cryptographers Problem studies how to perform a secure multi-party computation of the boolean-OR function. David Chaum first proposed this problem in the early 1980s and used it as an illustrative example to show that it was possible to send anonymous messages with unconditional sender and recipient untraceability.

Three cryptographers gather around a table for dinner. The waiter informs them that the meal has been paid for by someone, who could be one of the cryptographers or the National Security Agency. The cryptographers respect each other's right to make an anonymous payment, but want to find out whether the NSA paid.

In this case we concern n participants of computation, so we exceed original Chaum's problem, which shows solution for 3 participants.

#### 1.2 Implementation requirements

The following requirements can be defined in terms of problem solving:
 1. Every participant anonymity must be granted.
 2. Communication between users must be encrypted.
 3. Every message verification must be provided.
 4. Solution must be available for all participants.

The following requirements can be defined in terms of technological constraints:
 1. Communication via https protocol.
 2. System works on a server which is the channel for every participant message exchange.
 3. Server handles message verification.
 4. Server has no knowledge about result.

### 2. Solution discussion

#### 2.1 Dining Cryptographers network

Original Chaum's solution is realized in two rounds:

###### Round 1.

In the first round, every two cryptographers establish a shared one-bit secret, say by tossing a coin behind a menu so that only two cryptographers see the outcome in turn for each two cryptographers.

###### Round 2.

In the second stage, each cryptographer publicly announces a bit, which is:
 - if they didn't pay for the meal, the exclusive OR (XOR) of the two shared bits they hold with their two neighbours,
 - if they did pay for the meal, the opposite of that XOR.

If the result is 0, it implies that none of the cryptographers paid (so the NSA must have paid the bill). Otherwise, one of the cryptographers paid, but their identity remains unknown to the other cryptographers.

This solution does not prevent:
- Collisions
- Message disruption

Also its complexity is a problem when there are a lot of participants.

#### 2.2 2-Round Anonymous Veto Network

This protocol presents an efficient solution to the Dining cryptographers problem.

Participants agree on a group `G` with generator `g` in which the DLP is hard. This protocol is realized also in two rounds:

###### Round 1.

Each participant selects random x from group and sends `g^x` and zero-knowledge proof of `x`.

###### Round 2.

They computes `g^y` in such a way:

![gy](\gy.svg)

when `i` is the index of calculating participant.

Then participant decide:
- to set `c = x`, when want to send 'no veto'.
- to set `c` a random value, when want to send 'veto'.

Then `g^(yc)` is published together with zero-knowledge proof of `c`.

Result of the computation can be easily calulated by every participant. If ![result](\result.svg), then one of the participants vetoed.

Since it is more efficient than DC-network, it was used in presented solution.

### 3. Cryptographic components

#### 3.1 TLS communication

Is a cryptographic protocol that provides communications security over a computer network. Several versions of the protocols find widespread use in applications such as web browsing, email, instant messaging, and voice over IP. Websites are able to use TLS to secure all communications between their servers and web browsers. In the case of the project design traffic between clients and server is secured by TLS.

TLS is using public key infrastructure and AES encryption. Standard TSL procedure:

- The handshake begins when a client connects to a TLS-enabled server requesting a secure connection and the client presents a list of supported cipher suites.
- From this list, the server picks a cipher and hash function that it also supports and notifies the client of the decision.
- The server usually then provides identification in the form of a digital certificate. The certificate contains the server name, the trusted certificate authority that vouches for the authenticity of the certificate, and the server's public encryption key.
- The client confirms the validity of the certificate before proceeding.
- To generate the session keys used for the secure connection, the client either:
  - encrypts a random number with the server's public key and sends the result to the server (which only the server should be able to decrypt with its private key); both parties then use the random number to generate a unique session key for subsequent encryption and decryption of data during the session
  - uses Diffie–Hellman key exchange to securely generate a random and unique session key for encryption and decryption that has the additional property of forward secrecy: if the server's private key is disclosed in future, it cannot be used to decrypt the current session, even if the session is intercepted and recorded by a third party.


#### 3.2 Zero-konowledge proof

In cryptography, a zero-knowledge proof or zero-knowledge protocol is a method by which one party can prove to another party that she knows a value x, without conveying any information apart from the fact that she knows the value x. Good example of ZKP, which can be easily applied to this problem was mentioned [here](https://link.springer.com/chapter/10.1007%2F3-540-39118-5_13).

### 4. Implementation details

#### 4.1 Structural

Solution will be implemented in Python programming language. I will contain server and clients application. Server represents table and safe communication channel and clients represent cryptographers. TLS layer will be implemented using Flask framework.

#### 4.2 Behavioral

Clients will be communicating with HTTPS server in order to perform protocol steps. Every step will be implemented as TLS-secured endpoint which accepts POST requests. Zero knowledge proof details will be implemented as [here](https://link.springer.com/chapter/10.1007%2F3-540-39118-5_13).

### 3. References
 - [David Chaum, The Dining Cryptographers Problem:
Unconditional Sender and Recipient Untraceability](http://www.cs.cornell.edu/people/egs/herbivore/dcnets.html)
 - [David Chaum, An Improved Protocol for Demonstrating Possession of Discrete Logarithms and Some Generalizations](https://link.springer.com/chapter/10.1007%2F3-540-39118-5_13)
