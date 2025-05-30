select ai.id,
    a.nombre,
    a.nivel,
    ai.codigo,
    u.nombre as nombre_docente,
    u.apellido_paterno
from "Core_asignaturaimpartida" ai
    join "Core_asignatura" a on ai.asignatura_id = a.id
    join "Core_docente" d on ai.docente_id = d.usuario_id
    join "Core_usuario" u on d.usuario_id = u.auth_user_id;