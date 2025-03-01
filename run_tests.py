import pytest
import sys

def main():
    """Lance tous les tests avec pytest"""
    args = [
        "tests",  # dossier des tests
        "-v",     # mode verbeux
        "--tb=short",  # format court des tracebacks
    ]
    
    # Ajout des arguments de ligne de commande
    args.extend(sys.argv[1:])
    
    # Exécution des tests
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main())
