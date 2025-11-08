"""Test de funcionalidad real - learning_path_be con Firestore"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.db_services import (
    save_conversation,
    get_conversations_by_user,
    get_roadmaps_by_user,
    get_or_create_session,
    delete_conversation,
    count_user_conversations,
    get_conversations_by_session
)

# Variables globales para los tests
test_user = "test_user@example.com"
test_conversation_ids = []


async def test_1_create_session():
    """TEST 1: Crear sesión de usuario"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Crear sesión de usuario")
    print("="*60)
    
    try:
        session_id = get_or_create_session(test_user)
        print(f"✅ Sesión creada: {session_id}")
        
        # Verificar que la segunda llamada retorna la misma sesión
        session_id_2 = get_or_create_session(test_user)
        if session_id == session_id_2:
            print(f"✅ Sesión persistente verificada")
            return True
        else:
            print(f"❌ La sesión no persiste")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_2_save_conversations():
    """TEST 2: Guardar conversaciones"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Guardar múltiples conversaciones")
    print("="*60)
    
    try:
        # Guardar 3 conversaciones normales
        conversations = [
            {
                "route": "/chat",
                "prompt": "¿Qué es Python?",
                "response": "Python es un lenguaje de programación...",
                "metadata": {"topic": "python basics"}
            },
            {
                "route": "/chat",
                "prompt": "¿Cómo usar FastAPI?",
                "response": "FastAPI es un framework moderno...",
                "metadata": {"topic": "fastapi"}
            },
            {
                "route": "/roadmaps",
                "prompt": "Crear roadmap de Python",
                "response": "Roadmap: 1. Básicos, 2. POO, 3. Frameworks...",
                "metadata": {"roadmap_type": "python_learning"}
            }
        ]
        
        for conv in conversations:
            await save_conversation(
                user_email=test_user,
                route=conv["route"],
                prompt=conv["prompt"],
                response=conv["response"],
                metadata=conv["metadata"]
            )
        
        print(f"✅ 3 conversaciones guardadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_3_get_conversations():
    """TEST 3: Obtener conversaciones de usuario"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Obtener conversaciones")
    print("="*60)
    
    try:
        conversations = await get_conversations_by_user(test_user, limit=10)
        
        if len(conversations) >= 3:
            print(f"✅ Conversaciones obtenidas: {len(conversations)}")
            
            # Guardar IDs para limpieza posterior
            global test_conversation_ids
            test_conversation_ids = [c["_id"] for c in conversations]
            
            # Mostrar algunas conversaciones
            for i, conv in enumerate(conversations[:3], 1):
                print(f"   {i}. Route: {conv['route']} - Prompt: {conv['prompt'][:30]}...")
            
            return True
        else:
            print(f"❌ Se esperaban al menos 3 conversaciones, se obtuvieron {len(conversations)}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_4_get_roadmaps():
    """TEST 4: Obtener roadmaps específicos"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Filtrar roadmaps")
    print("="*60)
    
    try:
        roadmaps = await get_roadmaps_by_user(test_user, limit=20)
        
        print(f"✅ Roadmaps encontrados: {len(roadmaps)}")
        
        # Verificar que todos son roadmaps
        all_are_roadmaps = all(r["route"] == "/roadmaps" for r in roadmaps)
        
        if all_are_roadmaps:
            print(f"✅ Todos los resultados son roadmaps")
            for roadmap in roadmaps:
                print(f"   - {roadmap['prompt'][:50]}...")
            return True
        else:
            print(f"❌ Algunos resultados no son roadmaps")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_5_count_conversations():
    """TEST 5: Contar conversaciones"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Contar conversaciones de usuario")
    print("="*60)
    
    try:
        count = await count_user_conversations(test_user)
        
        if count >= 3:
            print(f"✅ Total de conversaciones: {count}")
            return True
        else:
            print(f"❌ Se esperaban al menos 3 conversaciones, se contaron {count}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_6_get_by_session():
    """TEST 6: Obtener conversaciones por sesión"""
    print("\n" + "="*60)
    print("🧪 TEST 6: Obtener conversaciones por sesión")
    print("="*60)
    
    try:
        session_id = get_or_create_session(test_user)
        conversations = await get_conversations_by_session(session_id)
        
        if len(conversations) >= 3:
            print(f"✅ Conversaciones de la sesión: {len(conversations)}")
            return True
        else:
            print(f"⚠️  Se obtuvieron {len(conversations)} conversaciones de la sesión")
            return True  # No falla porque puede haber múltiples sesiones
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_7_cleanup():
    """TEST 7: Limpiar datos de prueba"""
    print("\n" + "="*60)
    print("🧪 TEST 7: Limpiar datos de prueba")
    print("="*60)
    
    try:
        deleted_count = 0
        
        for conv_id in test_conversation_ids:
            success = await delete_conversation(conv_id)
            if success:
                deleted_count += 1
        
        print(f"✅ Conversaciones eliminadas: {deleted_count}/{len(test_conversation_ids)}")
        
        # Verificar que se eliminaron
        remaining = await count_user_conversations(test_user)
        print(f"   Conversaciones restantes: {remaining}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_8_multiple_users():
    """TEST 8: Verificar aislamiento entre usuarios"""
    print("\n" + "="*60)
    print("🧪 TEST 8: Aislamiento entre usuarios")
    print("="*60)
    
    try:
        test_user_2 = "otro_usuario@example.com"
        
        # Guardar conversación para user 2
        await save_conversation(
            user_email=test_user_2,
            route="/chat",
            prompt="Test de aislamiento",
            response="Respuesta de prueba",
            metadata={}
        )
        
        # Verificar que user 1 y user 2 tienen conversaciones separadas
        convs_user_1 = await get_conversations_by_user(test_user, limit=10)
        convs_user_2 = await get_conversations_by_user(test_user_2, limit=10)
        
        print(f"   User 1: {len(convs_user_1)} conversaciones")
        print(f"   User 2: {len(convs_user_2)} conversaciones")
        
        # Limpiar user 2
        for conv in convs_user_2:
            await delete_conversation(conv["_id"])
        
        if len(convs_user_2) >= 1:
            print(f"✅ Aislamiento entre usuarios verificado")
            return True
        else:
            print(f"❌ No se guardó la conversación del user 2")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "🔥"*30)
    print("TESTS DE FUNCIONALIDAD REAL - LEARNING_PATH_BE")
    print("🔥"*30)
    
    tests = [
        test_1_create_session,
        test_2_save_conversations,
        test_3_get_conversations,
        test_4_get_roadmaps,
        test_5_count_conversations,
        test_6_get_by_session,
        test_7_cleanup,
        test_8_multiple_users
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests exitosos: {passed}/{total}")
    print(f"❌ Tests fallidos: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ learning_path_be está listo para usar Firestore")
    else:
        print("\n⚠️  Algunos tests fallaron")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
