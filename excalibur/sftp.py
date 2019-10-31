class SFTPConnector:

    def __init__(self, host, username, password, port=22):
        # late import to avoid some os doesn't support paramiko
        import paramiko
        transport = paramiko.Transport((host, port))
        transport.start_client()
        transport.auth_password(username, password)
        client = paramiko.SFTPClient.from_transport(transport)
        self.client = client

    def list_files(self, remotepath):
        return self.client.listdir(remotepath)  # list all files in a dir

    def open_file(self, remotepath):
        return self.client.open(remotepath)  # opens the file

    def stat(self, remotepath):
        return self.client.stat(remotepath)  # check if remote path exists

    def list_files_attr(self, remotepath):
        return self.client.listdir_attr(remotepath)  # list attribute of a dir

    def copy(self, remote_path, local_path):
        return self.client.get(remote_path, local_path)  # download file to local_path
