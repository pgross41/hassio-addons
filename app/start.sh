#!/bin/bash

# Run dovecot
echo Starting dovecot
dovecot

# Run postfix in the foreground
echo Starting postfix
postfix start-fg
