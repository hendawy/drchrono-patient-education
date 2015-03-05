import drchrono

# If you want to authorize with the access token (which will fetch the oauth token).
#drc_client = drchrono.DRC(
        #api_url="https://staging.drchrono.com/api/",
        #api_key="",
        #client_id="",
        #client_secret="",
        #access_token="",
        #ssl_verify=False,
#)

# If you want to authorize with the oauth token.
drc_client = drchrono.DRC(
        api_url="https://drchrono.com/api/",
        api_key="",
        client_id="",
        client_secret="",
        oauth_token="",
        ssl_verify=False,
)

# Retrieves information about the doctor who is currently logged in.
print drchrono.Doctor.retrieve(client=drc_client, id=45375)
print "\n"

# Retrieves information about the doctor who is currently logged in. Only returns the first_name, last_name and email fields
print drchrono.Doctor.retrieve(client=drc_client, id=45375, fields=["first_name", "last_name", "email"])
print "\n"

# Retrieve all doctors that the currently logged in doctor has access to. Typically these are doctors in the logged in doctor's practice group.
print drchrono.Doctor.all(client=drc_client)
print "\n"

# Retrieve all appointments belonging to the currently logged in doctor and the ones belonging to doctors in their practice group.
print drchrono.Appointment.all(client=drc_client)
print "\n"
