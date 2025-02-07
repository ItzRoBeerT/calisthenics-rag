## Preguntas sobre el procesamiento del lenguaje natural natural

---

1. ¿Qué uso se hace del procesamiento del lenguaje natural?
El procesamiento del lenguaje natural se utiliza para interpretar las consultas de los usuarios, extraer y procesar información contextual de documentos, y generar respuestas o rutinas personalizadas mediante un modelo de lenguaje.

En este caso, lo hemos utilizado en conjunto con un RAG para que el modelo de leguaje pueda responder a las preguntas del usuario, en caso de que el usuario pregunte sobre un tema que no se especifíca en el documento, el modelo no podrá responderle a la pregunta (respondiendo que no conoce la respuesta).

2. ¿Por qué es útil utilizarlo?
Es útil porque permite a las máquinas comprender y procesar el lenguaje humano, facilitando respuestas personalizadas y la extracción eficiente de información relevante de grandes volúmenes de datos como es el caso de este proyecto.

Además, otro ejemplo que también utiliza este proyecto del uso del procesamiento de lenguaje natural es la capacidad de que con un prompt bien definido, puedes lograr que un modelo de lenguaje genere un diccionario para una acción concreta (en este caso es para montar una tabla de rutina a partir de un diccionario concreto).

---
## Detalles técnicos

Para la realización de este proyecto se ha utlizado el modelo `google/gemini-flash-1.5`, lo he utilizado debido a que posee una gran capacidad de contexto, una latencia bastante baja para tener una respuesta más rápida y tiene unos costes muy baratos. Puedes ver más detalles si haces click [aquí](https://openrouter.helicone.ai/google/gemini-flash-1.5-8b)

También he utilizado `PyPDFLoader` paa cargar el pdf y poder generar la documentación para el modelo de lenguaje.

En cuanto a la tool, he creado mi propia tool personalizada llamada `generate_routine_pdf` la cual se encarga de generar una tabla con los días de la semana para que el modelo de lenguaje pueda generar un pdf con la rutina. Hay que destacar que por ahora generará 3 tablas separando los días de la semana ya que si la dejo en una única tabla no se puede leer por el tamaño de las celdas asi que por el momento he dejado esta solución.

La tabla se genera a partir de un diccionario que el modelo de lenguaje generará si se le pasa la accion 'generar rutina' o 'crear rutina' en caso contrario realizará el RAG del documento para responder las preguntas del usuario, en caso de que el modelo de lenguaje no conozca la respuesta a la pregunta (según el documento) responderá que no conoce dicha información.

Una vez se ha generado el pdf, he creado una función para subir el mismo a un bucket en este caso de supabase, simplemente necesitas añadir tus credenciales al .env y llamar a la función `subir_pdf_a_supabase` con el nombre del documento (buscará en la carpeta files/`nombre_del_documento`).

---
## Diagrama conversacional de mermaid
```Mermaid
sequenceDiagram
    participant U as Usuario
    participant G as Interfaz Gradio
    participant C as Chatbot (main.py)
    participant L as LLM (ChatOpenAI)
    participant V as VectorStore (RAG)
    participant T as generate_routine_pdf (custom_tools)
    participant S as SupabaseUploader (functions)

    U->>G: Envía mensaje
    G->>C: Llama a chatbot(message, history)
    alt El mensaje indica "generar/crear rutina"
        C->>U: "🤔 Analizando el contexto y preparando respuesta..."
        C->>U: "🏋️ Generando rutina de entrenamiento..."
        C->>L: Envía prompt para generar un diccionario de ejercicios
        L-->>C: Responde con diccionario (texto plano)
        C->>C: Parsea el diccionario (ast.literal_eval)
        C->>T: Invoca generate_routine_pdf con el diccionario
        T-->>C: Retorna figura con la tabla de rutina
        C->>C: Guarda la figura como PDF en la carpeta ./files/
        C->>S: Llama a subir_pdf_a_supabase(pdf_name)
        S-->>C: Confirma la subida a Supabase
        C->>U: "Rutina generada y subida a supabase con éxito 🎉"
    else El mensaje es una consulta general
        C->>V: Ejecuta similarity_search(message) para obtener contexto
        V-->>C: Retorna documentos relevantes (fragmentos del manual)
        C->>L: Envía prompt que incluye contexto y la pregunta
        L-->>C: Genera respuesta basada en el contexto
        C->>U: Envía la respuesta generada
    end

```

