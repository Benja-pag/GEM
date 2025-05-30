SELECT *
FROM "Core_estudiante" e
    JOIN "Core_usuario" u ON e."usuario_id" = u."auth_user_id";