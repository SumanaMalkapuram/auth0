function (user, context, callback) {
  var _ = require('lodash');

  var DEFAULT_ROLE = "other";
  var roleToscopeMapping = {
    parent: ["offline_access", "read:cards", "delete:cards", "add:balance", "delete:balance", "read:balance"],
    child: ["offline_access", "read:cards", "delete:balance", "read:balance"],
    other: ["offline_access", "read:cards", "read:balance"]
  };

  var role = DEFAULT_ROLE;
  if (user && !!user.user_metadata && !!user.user_metadata.role) {
    var given_role = user.user_metadata.role;
    // check if the given role is supported in the mapping else default to DEFAULT_ROLE
    role = _.has(roleToscopeMapping, given_role)? given_role: DEFAULT_ROLE;
  } else {
    // if no role is specified throw an error
    return callback(new UnauthorizedError('Missing role for the user'));
  }

  var req = context.request;
  var requested_scopes = (req.query && req.query.scope) || (req.body && req.body.scope);
  requested_scopes = (requested_scopes && requested_scopes.split(" ")) || [];

  context.accessToken.scope = _.intersection(requested_scopes, roleToscopeMapping[role]);

  callback(null, user, context);
}
