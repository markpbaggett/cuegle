# Cuegle

Experiments with aggregrating content from Digital Library of Tennessee content providers via a 
[IIIF Change Discovery 1.0](https://iiif.io/api/discovery/1.0/) endpoint.

## About

The Cuegle is a three-eyed monster from Cantabrarian folklore that can see the past, present, and future.

The name is apropos for the Digital Library of Tennessee thinking about past activities in DLTN repositories available 
via a Change Discovery endpoint and how we might aggregate those to deliver the future of the Digital Library of
Tennessee.

**Note**: This is not intended to be used for production or really anything specific at all.

Instead, this is help us imagine what an aggregation system might look like, what it would need to do to grab data from 
an external service, and store it in an index.

## What's here

Not much. 

The `change_discovery` package aims to try to do things for aggregation following the Change Discovery 
specification. It doesn't do that yet.

The `mongo` package serves as a mechanism for writing data about these things to a mongo database solely for the purpose
of thinking about a data model and how an aggregator would need to interact and update and index.

