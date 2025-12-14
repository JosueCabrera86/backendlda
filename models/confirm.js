import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://laquetzfsftmujmugeos.supabase.co";
const SUPABASE_SERVICE_ROLE_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhcXVldHpmc2Z0bXVqbXVnZW9zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTM0NzUyNCwiZXhwIjoyMDgwOTIzNTI0fQ.EkqBCbmvzbxQXWmAWsg5EJZT7LIiSCvvVhlr7nE5j9I";

const supabaseAdmin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

async function confirmarTodosLosUsuarios() {
  try {
    // 1️⃣ Obtener todos los usuarios (hasta 1000)
    const { data, error } = await supabaseAdmin.auth.admin.listUsers({
      limit: 1000,
    });

    if (error) {
      console.error("Error listando usuarios:", error);
      return;
    }

    const users = data?.users; // ✅ data.users es el array real

    if (!users || users.length === 0) {
      console.log("No hay usuarios para procesar.");
      return;
    }

    for (const user of users) {
      if (!user.email_confirmed_at) {
        const { error: updateError } =
          await supabaseAdmin.auth.admin.updateUserById(user.id, {
            email_confirmed_at: new Date().toISOString(),
          });

        if (updateError)
          console.error(`Error confirmando ${user.email}:`, updateError);
        else console.log(`Usuario confirmado: ${user.email}`);
      } else {
        console.log(`Usuario ya confirmado: ${user.email}`);
      }
    }

    console.log("Todos los usuarios procesados.");
  } catch (err) {
    console.error("Error general:", err);
  }
}

// Ejecutar
confirmarTodosLosUsuarios();
