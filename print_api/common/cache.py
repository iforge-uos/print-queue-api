import json

import redis


class RedisCache(object):
    """
    Redis Cache Class
    """

    def __init__(self, uri, ex):
        """
        Constructor
        """

        # Parse the connection string for the various components
        self.r = redis.StrictRedis.from_url(uri)
        self.ex = ex
        self.prefix = "print_api_role_cache:"

    def store_user_roles(self, user_id, user_roles):
        """
        Store user roles, stores the user id and a list of the role names they have
        """
        user_role_names = []

        for user_role in user_roles:
            if user_role.role is None:
                continue  # This is the line that is throwing the error
            user_role_names.append(user_role.role.name)

        serialized_roles = json.dumps(user_role_names)
        key = self.prefix+str(user_id)
        self.r.set(key, serialized_roles, ex=self.ex)

    def store_user_permissions(self, user_id, user_roles):
        """
        Store user permissions, stores the user id and a list of the permission names they have
        """
        user_permission_names = []

        for user_role in user_roles:
            if user_role.role is None:
                continue
            for permission in user_role.role.permissions:
                user_permission_names.append(permission.name)

        serialized_permissions = json.dumps(user_permission_names)
        key = self.prefix+str(user_id)
        self.r.set(key, serialized_permissions, ex=self.ex)

    def get_user_roles(self, user_id) -> list[str]:
        """
        Get user roles
        """
        key = self.prefix + str(user_id)
        serialized_roles = self.r.get(key)
        if serialized_roles is None:
            return []
        return json.loads(serialized_roles)

    def get_user_permissions(self, user_id) -> list[str]:
        """
        Get user permissions
        """
        key = self.prefix + str(user_id)
        serialized_permissions = self.r.get(key)
        if serialized_permissions is None:
            return []
        return json.loads(serialized_permissions)

    def has_user_roles(self, user_id):
        """
        Check if user roles exist
        """
        key = self.prefix + str(user_id)
        return self.r.exists(key)

    def has_user_permissions(self, user_id):
        """
        Check if user permissions exist
        """
        key = self.prefix + str(user_id)
        return self.r.exists(key)

    def delete_user_roles(self, user_id):
        """
        Delete user roles
        """
        key = self.prefix + str(user_id)
        self.r.delete(key)

    def delete_user_permissions(self, user_id):
        """
        Delete user permissions
        """
        key = self.prefix + str(user_id)
        self.r.delete(key)
