# Write stdin to file
input_buffer="/app/handle_email_input_buffer";
cat > "$input_buffer";

# Upload it to Dropbox
/usr/bin/python3 email2dropbox.py\
 --access_token "TODO"\
 "$input_buffer";

# Forward the message to gmail
/usr/bin/python3 email2email.py\
 --username "TODOexternalemail@gmail.com"\
 --password "todo"\
 --from_addr "TODOexternalemail@gmail.com"\
 --to_addr "TODOexternalemail@gmail.com"\
 "$input_buffer";
