from langchain_core.tools import tool
import matplotlib.pyplot as plt
import pandas as pd

@tool
def generate_routine_pdf(exercises_dict: dict, rest_days: list[str] = ['Domingo']) -> plt.Figure:
    """
    Genera un PDF con una tabla de rutina de entrenamiento dividida en tres secciones:
    - Primera tabla: Lunes y Martes.
    - Segunda tabla: Miércoles y Jueves.
    - Tercera tabla: Viernes a Domingo.

    Parameters:
    exercises_dict (dict): Diccionario con categorías de ejercicios como claves y listas de ejercicios como valores.
    rest_days (list): Lista de días de descanso (en español).

    Returns:
    plt.Figure: Figura con la rutina dividida en tres tablas.
    """
    # Crear figura con 3 subgráficos (tablas separadas)
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))

    # Ocultar ejes en cada subgráfico
    for ax in axes:
        ax.axis('off')

    # Lista de días de la semana
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Dividir días en tres grupos
    first_table_days = days[:2]   # Lunes y Martes
    second_table_days = days[2:4]  # Miércoles y Jueves
    third_table_days = days[4:]   # Viernes a Domingo

    def create_table(ax, selected_days):
        """Genera una tabla con los días seleccionados."""
        if not selected_days:
            return

        max_exercises = max(len(ex) for ex in exercises_dict.values()) if exercises_dict else 3

        # Inicializar matriz de datos con "DESCANSO" en días de descanso
        data = [['DESCANSO' if day in rest_days else '' for day in selected_days] for _ in range(max_exercises)]

        # Distribuir ejercicios en los días seleccionados (solo si no son de descanso)
        day_index = 0
        for category, exercises in exercises_dict.items():
            if day_index >= len(selected_days):
                break

            current_day = selected_days[day_index]

            # Saltar días de descanso
            if current_day in rest_days:
                continue

            day_column = selected_days.index(current_day)

            for i, exercise in enumerate(exercises):
                data[i][day_column] = exercise

            day_index += 1

        # Crear DataFrame
        df = pd.DataFrame(data, columns=selected_days)

        # Crear tabla en el eje correspondiente
        table = ax.table(cellText=df.values,
                         colLabels=df.columns,
                         loc='center',
                         cellLoc='center')

        # Estilizar la tabla
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.5)
        table.auto_set_column_width([i for i in range(len(selected_days))])

        # Colorear encabezados y días de descanso
        for k, cell in table._cells.items():
            if k[0] == 0:  # Encabezados
                cell.set_facecolor('#4472C4')
                cell.set_text_props(color='white')
            elif df.values[k[0] - 1][k[1]] == 'DESCANSO':
                cell.set_facecolor('#FFE699')

    # Generar las tres tablas en los subgráficos
    create_table(axes[0], first_table_days)  # Lunes y Martes
    create_table(axes[1], second_table_days)  # Miércoles y Jueves
    create_table(axes[2], third_table_days)  # Viernes a Domingo

    fig.tight_layout()
    return fig

# Example usage
exercises = {
    1: ['Press banca: 3x10', 'Aperturas: 3x10', 'Push ups: 3:10'],
    2: ['Squats: 3x10', 'Lunges: 3x30', 'Leg press: 3x10'],
    3: ['Pull ups: 3x10', 'Remo: 3x10', 'Dominadas: 3x10'],
    4: ['Curl biceps: 3x10', 'Extension triceps: 3x10', 'Hammer curls: 3x10'],
    5: ['Press militar: 3x10', 'Elevaciones laterales: 3x10', 'Face pulls: 3x10'],
    6: ['Press banca: 3x10', 'Aperturas: 3x10', 'Push ups: 3x10'],
}

#fig = generate_routine_pdf(exercises, rest_days=['Domingo'])