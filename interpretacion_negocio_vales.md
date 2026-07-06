# Interpretación ejecutiva del negocio de vales

Este documento funciona como base de conocimiento para los comentarios tipo IA del tablero de Valeras. Su objetivo es que la lectura de los indicadores no se limite a describir cifras, sino que conecte los datos con la lógica real del negocio: colocación, dispersión, canjes, cartera, mora, calidad, plazo, interés, herramientas de liquidación y concentración territorial.

## 1. Modelo de negocio

El negocio de vales es un modelo de crédito indirecto en el que la empresa otorga una línea de crédito a una distribuidora o distribuidor autorizado. La distribuidora administra la colocación de vales entre sus clientes finales, decide a quién asignar crédito dentro de su red, realiza el seguimiento de pago y liquida los abonos correspondientes en sucursal o caja.

Por esta razón, la operación debe analizarse en dos niveles: el desempeño de la distribuidora como responsable de una cartera y el comportamiento de los clientes finales que utilizan los vales. Una operación sana no es solamente la que dispersa más, sino la que logra crecer sin deteriorar la calidad de cartera.

## 2. Conceptos principales

Vale: crédito otorgado en papel o de forma digital, con pago quincenal y plazo determinado.

Tipo de vale: modalidad con la que se realiza la transacción. Puede ser Vale Tradicional, Vale App o Dispersión App.

Vale Tradicional: vale tramitado directamente en sucursal, donde también se entrega el dinero en efectivo.

Vale App: vale tramitado mediante aplicación móvil, con entrega del dinero en sucursal.

Dispersión App: vale tramitado mediante aplicación móvil, con depósito del dinero a la cuenta CLABE del cliente o usuario.

Canje: acto mediante el cual un vale se convierte en dinero para el cliente final.

Dispersión: monto entregado al cliente; considera capital, sin incluir interés.

Interés: costo financiero que paga el cliente por utilizar el monto del vale otorgado.

Plazo: duración del vale o crédito, medido en quincenas.

Fecha de vencimiento: fecha de término del plazo otorgado para un vale.

Liquidada: estatus que indica si todas las parcialidades fueron cubiertas. Si el crédito quedó pagado es “Sí”; de lo contrario es “No”.

Marca: unidad de negocio que otorga el financiamiento de los vales. Las marcas consideradas son Vale Amigo, Viva Vale y RapiVale.

## 3. Distribuidoras y cartera

La distribuidora autorizada es la figura central del modelo. Es la persona física facultada para otorgar vales a su grupo de clientes finales. Una distribuidora sana mantiene su cartera al corriente, conserva capacidad de colocar nuevos vales, cuenta con clientes activos pagando y no presenta deterioro relevante en mora.

Cliente o usuario es la persona física habilitada para disponer de los vales que la distribuidora le concede.

Distribuidora al corriente: distribuidora con 0 días de atraso o con alguna herramienta activa de regularización.

Distribuidora en mora: distribuidora con más de 0 días de atraso y sin herramienta activa.

Cliente al corriente: cliente que pertenece a una distribuidora al corriente.

Cliente en atraso: cliente que pertenece a una distribuidora en mora.

Mora: colocado neto asociado a distribuidoras con más de 0 días de atraso y sin herramienta activa.

Colocado financiero o cartera: monto otorgado a crédito mediante vales, normalmente con una tasa mayor a la del préstamo personal.

Colocado PP: préstamo personal o préstamo personal especial, monto otorgado a crédito con una tasa menor a la del financiero.

Colocado neto: suma de colocado financiero y colocado PP.

Colocado neto al corriente: colocado neto de distribuidoras con 0 días de atraso o con herramienta activa.

Calidad de cartera: porcentaje de colocado neto al corriente sobre colocado neto total. Una calidad alta indica control de recuperación; una calidad baja indica deterioro, presión de cobranza y riesgo financiero.

Status Mora VA: campo que indica si la distribuidora está en mora. Cuando está vacío, la distribuidora se considera al corriente; cuando contiene 1, indica atraso o mora.

## 4. Canje, renovación y vale sobre vale

El canje es la operación que convierte el vale en dinero. Los canjes muestran actividad comercial y profundidad de uso de la línea de crédito. La dispersión muestra el monto colocado y el canje promedio ayuda a entender el tamaño típico del crédito entregado.

La renovación aplica cuando el cliente tiene una compra activa próxima a liquidarse. Dependiendo de los canjes acumulados, puede aplicar en los últimos pagos pendientes. Al renovar, el saldo restante de la compra anterior se liquida automáticamente y se entrega al cliente la diferencia correspondiente.

El vale sobre vale aplica cuando el cliente desea realizar una nueva compra, tiene línea de crédito disponible, pero no desea renovar o no es elegible para renovación. El cliente puede tener múltiples vales activos siempre que cuente con línea disponible, no tenga morosidad y su línea revolvente lo permita.

La línea de crédito revolvente se libera conforme el cliente paga capital. Esta liberación es independiente del incremento de línea autorizado por número de canjes concluidos.

## 5. Categorías de distribuidora

Las categorías Bronce, Plata, Oro, Platino, Diamante y Embajadoras representan rangos de colocado y niveles de bonificación. A mayor categoría, mayor capacidad de colocación y mayor bonificación potencial, especialmente cuando el pago se realiza en días preferentes.

Una base concentrada en Bronce o Plata puede indicar oportunidad de crecimiento y desarrollo. Una base concentrada en Platino, Diamante o Embajadoras indica mayor capacidad comercial, pero también mayor exposición si la cartera se deteriora.

## 6. Pagos, bonificaciones y caída

Pago Omega y pago puntual son días con bonificación para la distribuidora. La bonificación disminuye conforme pasan los días del periodo de pago.

Pago a destiempo corresponde a días en los que los pagos efectuados no generan bonificación. Aunque el pago pueda ayudar a mantener activa la cartera, reduce eficiencia e incentivos.

Caída representa los días que determinan el inicio y fin de un corte operativo, principalmente los días 7 y 22 de cada mes. Al hablar “al corte”, la lectura representa una fotografía específica de la operación y no necesariamente una tendencia completa.

## 7. Herramientas de liquidación

Las herramientas son estatus asignados a una distribuidora para permitirle regularizarse, seguir colocando bajo control o contar con un plan de pago. Las principales herramientas son quebranto, consideración, reestructura y robo.

El quebranto aplica como mecanismo de recuperación para mora avanzada. El descuento aumenta conforme crecen los días de mora, porque el objetivo cambia de conservar margen a recuperar saldo.

La reestructura permite reorganizar pagos en varias quincenas. Puede aplicar con mora mínima o en condiciones especiales, siempre que exista gestión registrada y seguimiento operativo.

Estas herramientas no deben interpretarse como crecimiento comercial normal; son mecanismos de contención, recuperación o regularización.

## 8. Interpretación ejecutiva de indicadores

Cuando la dispersión crece y la calidad se mantiene alta, la lectura es favorable: la operación expande colocación sin deterioro relevante.

Cuando la dispersión crece pero la calidad baja, la lectura es de alerta: se está colocando más, pero con menor control de recuperación.

Cuando la dispersión cae y la calidad también cae, la lectura es crítica: existe menor actividad comercial y mayor presión de cobranza.

Cuando la dispersión cae pero la calidad mejora, puede tratarse de una etapa de contención, depuración o recuperación antes de volver a acelerar colocación.

Una sucursal con alto capital, alta tasa de ganancia y buena calidad es un punto fuerte. Una sucursal con alto capital y baja calidad es un foco prioritario de cobranza. Una sucursal con baja dispersión y buena calidad puede tener oportunidad comercial. Una sucursal con baja dispersión y mala calidad requiere revisión operativa antes de impulsar crecimiento.

## 9. Plazo y composición financiera

En la vista de plazo y composición, capital representa el monto efectivamente prestado, interés representa la ganancia financiera esperada y total representa capital más interés. La tasa de ganancia muestra la relación entre interés y capital. Los vales indican volumen de operaciones y el monto promedio por vale ayuda a entender el tamaño del crédito colocado.

Una tasa de ganancia alta es positiva si la cartera mantiene buena recuperación. Si la tasa alta convive con mora elevada, la ganancia esperada podría no materializarse.

El treemap financiero debe interpretarse por peso de capital y rentabilidad. Los cuadros más grandes concentran más capital colocado, por lo que cualquier deterioro en esos nodos tiene mayor impacto financiero. El color por tasa de ganancia permite distinguir dónde se genera mayor rendimiento esperado.

## 10. Instrucción general para la IA

Al interpretar el negocio de vales, no describas únicamente el valor de los indicadores. Relaciona colocación, dispersión, canjes, calidad de cartera, distribuidoras al corriente, distribuidoras en mora, mora, capital, interés, tasa de ganancia y plazo. Considera que una operación sana es aquella que crece en dispersión y canjes sin deteriorar la calidad de cartera.

Si la calidad baja, la mora sube o aumenta la proporción de distribuidoras en mora, el comentario debe marcar atención operativa. Si la dispersión aumenta junto con buena calidad y baja mora, el comentario debe destacar fortaleza comercial. Si el capital se concentra en pocas sucursales o zonas, señala concentración de riesgo u oportunidad según la calidad y tasa observada.

Usa lenguaje ejecutivo, claro y accionable, orientado a decisiones de cobranza, recuperación, contención o crecimiento.

## Bloques técnicos para el script

[BLOQUE:RESUMEN_CARTERA]
La lectura debe conectar tamaño de base, calidad de cartera y mora. Una operación sana no sólo tiene más distribuidoras o más dispersión; debe sostener una proporción alta de distribuidoras al corriente y controlar el deterioro. Si la calidad cae o la mora gana peso, la prioridad es cobranza, contención y seguimiento por sucursal.
[/BLOQUE]

[BLOQUE:ACTIVIDAD_COMERCIAL]
La dispersión representa capital entregado y los canjes representan operaciones realizadas. Un aumento de canjes con buena calidad indica expansión sana; un aumento de canjes con baja calidad puede señalar crecimiento riesgoso. El canje promedio permite entender el tamaño típico del crédito colocado.
[/BLOQUE]

[BLOQUE:MAPA_ESTRUCTURA]
El mapa debe usarse para ubicar concentración territorial de oportunidad y riesgo. Los puntos con mayor volumen y buena calidad son fortalezas replicables. Los puntos con alto volumen y baja calidad son prioridades de cobranza, porque concentran impacto financiero y operativo.
[/BLOQUE]

[BLOQUE:TABLA_RESUMEN]
La tabla permite priorizar decisiones. No debe leerse sólo como ranking: combina volumen, calidad, mora y dispersión para separar crecimiento sano, oportunidad comercial, focos de recuperación y zonas donde conviene contener colocación antes de acelerar.
[/BLOQUE]

[BLOQUE:PLAZO_COMPOSICION]
En plazo y composición, capital es monto prestado, interés es ingreso financiero esperado, total es capital más interés, tasa de ganancia es rentabilidad esperada y vales es volumen de operaciones. Una tasa alta es positiva sólo si el capital mantiene recuperación controlada; si el capital se concentra, ese nodo debe vigilarse por su impacto.
[/BLOQUE]

[BLOQUE:HERRAMIENTAS]
Las herramientas como quebranto, consideración, reestructura o robo son mecanismos de regularización y recuperación. No deben leerse como crecimiento comercial normal; sirven para contener deterioro, ordenar pagos y recuperar saldo.
[/BLOQUE]
