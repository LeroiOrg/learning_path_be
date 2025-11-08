"""
Test de integración simplificado - learning_path_be
Verifica que Firestore está correctamente configurado
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_1_firestore_connection():
    """TEST 1: Verificar conexión a Firestore"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Conexión a Firestore")
    print("="*60)
    
    try:
        from app.db.firestore_client import get_db
        
        db = get_db()
        
        if db:
            print(f"✅ Firestore conectado correctamente")
            print(f"   Tipo de cliente: {type(db).__name__}")
            return True
        else:
            print(f"❌ Firestore no conectado")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_2_save_and_retrieve():
    """TEST 2: Guardar y recuperar conversación"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Operaciones en Firestore")
    print("="*60)
    
    try:
        from app.services.db_services import save_conversation, get_conversations_by_user, delete_conversation
        
        test_user = "integration_test@example.com"
        
        async def run_test():
            # Guardar
            await save_conversation(
                user_email=test_user,
                route="/test",
                prompt="Test prompt",
                response="Test response",
                metadata={"test": True}
            )
            print(f"✅ Conversación guardada")
            
            # Recuperar
            conversations = await get_conversations_by_user(test_user, limit=10)
            
            if len(conversations) > 0:
                print(f"✅ Conversaciones recuperadas: {len(conversations)}")
                
                # Limpiar
                for conv in conversations:
                    await delete_conversation(conv["_id"])
                print(f"✅ Datos de prueba eliminados")
                
                return True
            else:
                print(f"❌ No se encontraron conversaciones")
                return False
        
        return asyncio.run(run_test())
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_3_db_services_imports():
    """TEST 3: Verificar imports en db_services"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Verificar que db_services usa Firestore")
    print("="*60)
    
    try:
        with open("app/services/db_services.py", "r", encoding='utf-8') as f:
            content = f.read()
        
        has_firestore = "from app.services.db_services_firestore import" in content
        has_pymongo = "from pymongo" in content or "import pymongo" in content
        
        if has_firestore and not has_pymongo:
            print(f"✅ db_services correctamente migrado")
            print(f"   ✅ Importa de db_services_firestore")
            print(f"   ✅ No usa pymongo directamente")
            return True
        else:
            print(f"❌ db_services tiene imports incorrectos:")
            if not has_firestore:
                print(f"   ❌ No importa db_services_firestore")
            if has_pymongo:
                print(f"   ❌ Todavía usa pymongo")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_4_query_collections():
    """TEST 4: Listar colecciones de Firestore"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Query a Firestore")
    print("="*60)
    
    try:
        from app.db.firestore_client import get_db
        
        db = get_db()
        collections = list(db.collections())
        
        print(f"✅ Query exitoso")
        print(f"   Colecciones: {len(collections)}")
        if len(collections) > 0:
            print(f"   Ejemplos: {[c.id for c in collections[:3]]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_5_app_can_import():
    """TEST 5: Verificar que la app se puede importar"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Importar aplicación")
    print("="*60)
    
    try:
        from app.main import app
        
        if app:
            print(f"✅ Aplicación FastAPI importada correctamente")
            return True
        else:
            print(f"❌ Error importando app")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🔥"*30)
    print("TESTS DE INTEGRACIÓN - LEARNING_PATH_BE")
    print("🔥"*30)
    
    tests = [
        test_1_firestore_connection,
        test_2_save_and_retrieve,
        test_3_db_services_imports,
        test_4_query_collections,
        test_5_app_can_import
    ]
    
    results = []
    for test in tests:
        result = test()
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
        print("✅ learning_path_be está correctamente migrado a Firestore")
        print("\n📝 Para probar endpoints HTTP, ejecuta:")
        print("   uvicorn app.main:app --reload --port 8080")
    else:
        print("\n⚠️  Algunos tests fallaron")
    
    print("="*60 + "\n")
