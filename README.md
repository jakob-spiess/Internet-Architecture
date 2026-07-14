# Distributed Git-Based Chat Application

A distributed chat application developed as part of the **Distributed Programming and Internet Architecture** course at the University of Basel.

## Overview

This project extends a Git-based peer-to-peer chat application with UDP broadcast communication and Conflict-Free Replicated Data Types (CRDTs) to achieve eventual consistency across multiple replicas.

The application allows participants to exchange messages without a central server while ensuring that all replicas eventually synchronize, even after temporary disconnections.

## Features

- Git-based storage for chat messages
- UDP broadcast for peer discovery and communication
- Last activity tracking for all participants
- Frontier computation using vector clocks
- Automatic replication of missing messages
- Eventual consistency across distributed replicas
- CRDT-based state synchronization
- Offline recovery and synchronization when peers reconnect

## Technologies Used

- Python
- Git
- UDP Sockets
- State-based CRDTs
- Vector Clocks

## How It Works

Each participant maintains a local Git repository containing the chat history. Replicas periodically broadcast their state using UDP packets, allowing other peers to:

- Track participant activity
- Compare replication frontiers
- Detect missing messages
- Automatically exchange and replicate missing commits

The system is designed so that all replicas eventually converge to the same state, even when some participants are temporarily offline.

## Git Integration

Git is used as the underlying storage and versioning mechanism for chat messages. Each message is stored as a Git commit, allowing the application to:

- Track message history
- Manage replication state
- Synchronize repositories between peers
- Maintain consistency across distributed replicas

## Project Status

Successfully completed all required tasks from Exercise 3, including:

- Last Activity Status via UDP Broadcast
- Frontier Computation using Vector Clocks
- UDP-based Git Message Replication
- Eventual consistency testing across multiple machines

## Author

Created as part of the **Distributed Programming and Internet Architecture (FS2024)** course at the University of Basel.
