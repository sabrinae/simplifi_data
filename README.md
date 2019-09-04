# simplifi_data_api
Python script connecting to the Simpli.fi API to pull campaigns and correlating information for each client

Simpli.fi API documentation: https://app.simpli.fi/apidocs

This script finds all campaigns for each client under our organization with a status of "Active" or "Pending" and the associated daily stats per campaign. Two separate API endpoints must be accessed to pull all of the information.
Script is automated on <a href="https://try.dominodatalab.com">Domino</a>
