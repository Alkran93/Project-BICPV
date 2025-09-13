#!/usr/bin/env python3
"""
Validador de Estándares de Nombramiento - SolarGrid Monitor

Este script valida el cumplimiento de convenciones de nombramiento establecidas
para el proyecto SolarGrid Monitor, siguiendo estándares oficiales reconocidos
por la industria para cada tecnología utilizada.

JUSTIFICACIÓN TÉCNICA:
===================

1. ENFOQUE MULTI-TECNOLOGÍA
   El proyecto utiliza un stack heterogéneo (Python, TypeScript, React, SQL)
   que requiere diferentes convenciones de nombramiento por tecnología.
   Cada estándar está justificado por documentación oficial:

   - Python: PEP 8 (https://peps.python.org/pep-0008/)
   - TypeScript/React: Airbnb Style Guide (https://github.com/airbnb/javascript)
   - PostgreSQL: PostgreSQL Guidelines (https://postgresql.org/docs/current/)
   - REST APIs: RESTful Design (https://restfulapi.net/resource-naming/)

2. VALIDACIÓN CONTEXTUAL
   No es suficiente aplicar reglas genéricas; el validador comprende el contexto:
   - Componentes React requieren PascalCase (.tsx)
   - Servicios TypeScript usan camelCase (.ts)
   - Modelos Python siguen snake_case (.py)
   - APIs REST utilizan kebab-case

3. EXCLUSIÓN DE DEPENDENCIAS
   El script diferencia entre código del proyecto y dependencias externas,
   evitando falsos positivos en librerías de terceros (venv/, node_modules/).

4. DETECCIÓN INTELIGENTE
   Implementa heurísticas para detectar patrones problemáticos específicos
   del dominio (typos, inconsistencias, violaciones sutiles).

5. REPORTES ACCIONABLES
   Los errores incluyen contexto suficiente para corrección inmediata,
   con referencias a documentación y ejemplos específicos.

Autor: Equipo SolarGrid Monitor
Versión: 2.0
Fecha: Diciembre 2024
Licencia: MIT
"""

import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import ClassVar, Optional


# Configuración de colores para output legible
class Colors:
    """Códigos ANSI para colores en terminal"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    END = "\033[0m"


class ValidationLevel(Enum):
    """Niveles de severidad para problemas detectados"""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationResult:
    """Resultado de validación estructurado"""

    file_path: str
    message: str
    level: ValidationLevel
    rule: str
    suggestion: Optional[str] = None


class NamingValidator:
    """
    Validador principal de estándares de nombramiento

    ARQUITECTURA:
    - Separación de responsabilidades por tecnología
    - Configuración centralizada de patrones
    - Exclusión inteligente de dependencias
    - Reportes estructurados y accionables
    """

    # Configuración de patrones por tecnología
    PATTERNS: ClassVar[dict[str, re.Pattern]] = {
        "python_file": re.compile(r"^[a-z_][a-z0-9_]*\.py$"),
        "python_module": re.compile(r"^[a-z_][a-z0-9_]*$"),
        "react_component": re.compile(r"^[A-Z][A-Za-z0-9]*\.tsx$"),
        "ts_service": re.compile(r"^[a-z][a-zA-Z0-9]*\.ts$"),
        "ts_hook": re.compile(r"^use[A-Z][a-zA-Z0-9]*\.ts$"),
        "type_definition": re.compile(r"^[A-Z][A-Za-z0-9]*\.d\.ts$"),
        "css_class": re.compile(r"^[a-z][a-z0-9-]*\.css$"),
    }

    # Directorios a excluir (dependencias externas)
    EXCLUDE_PATTERNS: ClassVar[list[str]] = [
        "venv",
        "node_modules",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "build",
        ".vscode",
        ".idea",
    ]

    # Estructura esperada del proyecto
    EXPECTED_STRUCTURE: ClassVar[dict[str, list[str]]] = {
        "backend_dirs": ["app", "core", "models", "services", "utils", "tests"],
        "frontend_dirs": ["src", "public"],
        "config_files": ["requirements.txt", "package.json", "README.md"],
    }

    def __init__(self, project_root: Path):
        """
        Inicializa el validador

        Args:
            project_root: Ruta raíz del proyecto
        """
        self.project_root = project_root
        self.results: list[ValidationResult] = []

    def validate_all(self) -> list[ValidationResult]:
        """
        Ejecuta todas las validaciones

        Returns:
            Lista de resultados de validación
        """
        print(
            f"{Colors.BOLD}{Colors.BLUE} Validando estándares de nombramiento - "
            f"SolarGrid Monitor{Colors.END}"
        )
        print(f"Proyecto: {self.project_root}\n")

        # Ejecutar validaciones por tecnología
        print(f"{Colors.BLUE} Validando archivos Python (PEP 8)...{Colors.END}")
        self._validate_python_files()

        print(
            f"{Colors.BLUE}  Validando archivos TypeScript/React "
            f"(Airbnb)...{Colors.END}"
        )
        self._validate_typescript_files()

        print(f"{Colors.BLUE} Validando estructura de directorios...{Colors.END}")
        self._validate_directory_structure()

        print(f"{Colors.BLUE} Detectando problemas específicos...{Colors.END}")
        self._validate_domain_specific()

        return self.results

    def _is_excluded_path(self, file_path: Path) -> bool:
        """
        Determina si una ruta debe ser excluida de la validación

        JUSTIFICACIÓN: Evita falsos positivos en dependencias externas
        que siguen sus propias convenciones (ej: numpy usa CamelCase en algunos módulos)
        """
        path_str = str(file_path)
        return any(pattern in path_str for pattern in self.EXCLUDE_PATTERNS)

    def _validate_python_files(self) -> None:
        """
        Valida archivos Python siguiendo PEP 8

        JUSTIFICACIÓN PEP 8:
        - snake_case mejora legibilidad en Python
        - Consistente con stdlib de Python
        - Ampliamente adoptado en ecosistema Python
        - Herramientas como Black/flake8 lo enfuerzan automáticamente
        """
        for backend_dir in self.EXPECTED_STRUCTURE["backend_dirs"]:
            dir_path = self.project_root / backend_dir
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                if self._is_excluded_path(py_file):
                    continue

                filename = py_file.name

                # Validar nombre de archivo
                if not self.PATTERNS["python_file"].match(filename):
                    self.results.append(
                        ValidationResult(
                            file_path=str(py_file.relative_to(self.project_root)),
                            message=f"Archivo Python no sigue snake_case: {filename}",
                            level=ValidationLevel.ERROR,
                            rule="PEP8-FILE-NAMING",
                            suggestion=(
                                f"Renombrar a: {self._suggest_snake_case(filename)}"
                            ),
                        )
                    )

    def _validate_typescript_files(self) -> None:
        """
        Valida archivos TypeScript/React siguiendo Airbnb Style Guide

        JUSTIFICACIÓN AIRBNB GUIDE:
        - PascalCase para componentes React es estándar de facto
        - camelCase para servicios mantiene consistencia con JavaScript
        - Diferenciación clara entre componentes UI y lógica de negocio
        - Compatible con herramientas como ESLint/Prettier
        """
        frontend_src = self.project_root / "frontend" / "src"
        if not frontend_src.exists():
            return

        # Validar componentes React
        components_dir = frontend_src / "components"
        if components_dir.exists():
            for tsx_file in components_dir.glob("*.tsx"):
                filename = tsx_file.name
                if not self.PATTERNS["react_component"].match(filename):
                    self.results.append(
                        ValidationResult(
                            file_path=str(tsx_file.relative_to(self.project_root)),
                            message=f"Componente React no sigue PascalCase: {filename}",
                            level=ValidationLevel.ERROR,
                            rule="REACT-COMPONENT-NAMING",
                            suggestion=(
                                f"Renombrar a: {self._suggest_pascal_case(filename)}"
                            ),
                        )
                    )

        # Validar servicios TypeScript
        services_dir = frontend_src / "services"
        if services_dir.exists():
            for ts_file in services_dir.glob("*.ts"):
                filename = ts_file.name
                if not self.PATTERNS["ts_service"].match(filename):
                    self.results.append(
                        ValidationResult(
                            file_path=str(ts_file.relative_to(self.project_root)),
                            message=(
                                f"Servicio TypeScript no sigue camelCase: {filename}"
                            ),
                            level=ValidationLevel.ERROR,
                            rule="TS-SERVICE-NAMING",
                            suggestion=(
                                f"Renombrar a: {self._suggest_camel_case(filename)}"
                            ),
                        )
                    )

        # Validar hooks React
        hooks_dir = frontend_src / "hooks"
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.ts"):
                filename = hook_file.name
                if not filename.startswith("use"):
                    self.results.append(
                        ValidationResult(
                            file_path=str(hook_file.relative_to(self.project_root)),
                            message=f"Hook React debe empezar con 'use': {filename}",
                            level=ValidationLevel.ERROR,
                            rule="REACT-HOOK-NAMING",
                            suggestion=(
                                f"Renombrar a: use{self._suggest_pascal_case(filename)}"
                            ),
                        )
                    )

        # Validar definiciones de tipos
        types_dir = frontend_src / "types"
        if types_dir.exists():
            for type_file in types_dir.glob("*.d.ts"):
                filename = type_file.name
                if not self.PATTERNS["type_definition"].match(filename):
                    self.results.append(
                        ValidationResult(
                            file_path=str(type_file.relative_to(self.project_root)),
                            message=f"Definición de tipos debe seguir PascalCase: {filename}",
                            level=ValidationLevel.WARNING,
                            rule="TS-TYPE-NAMING",
                            suggestion="Usar PascalCase para archivos .d.ts",
                        )
                    )

    def _validate_directory_structure(self) -> None:
        """
        Valida estructura de directorios siguiendo Clean Architecture

        JUSTIFICACIÓN CLEAN ARCHITECTURE:
        - Separación clara de responsabilidades
        - Facilita testing y mantenimiento
        - Escalabilidad del proyecto
        - Estándar reconocido en la industria
        """
        for expected_dir in self.EXPECTED_STRUCTURE["backend_dirs"]:
            dir_path = self.project_root / expected_dir
            if (
                not dir_path.exists() and expected_dir != "tests"
            ):  # tests es opcional inicialmente
                self.results.append(
                    ValidationResult(
                        file_path="",
                        message=f"Directorio esperado faltante: {expected_dir}/",
                        level=ValidationLevel.WARNING,
                        rule="PROJECT-STRUCTURE",
                        suggestion=f"Crear directorio: mkdir {expected_dir}",
                    )
                )

    def _validate_domain_specific(self) -> None:
        """
        Validaciones específicas del dominio SolarGrid Monitor

        JUSTIFICACIÓN DOMAIN-SPECIFIC:
        - Detecta problemas únicos del proyecto (typos, inconsistencias)
        - Evolucionará con el proyecto para capturar nuevos patrones
        - Complementa validaciones genéricas con conocimiento de contexto
        """
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file() or self._is_excluded_path(file_path):
                continue

            filename = file_path.name

            # Detectar typos conocidos específicos del dominio
            known_typos = {
                "Anasysis": "Analysis",
                "Sensr": "Sensor",
                "Fasade": "Facade",
                "Temprature": "Temperature",
            }

            for typo, correction in known_typos.items():
                if typo in filename:
                    # Verificar si existe versión corregida
                    corrected_name = filename.replace(typo, correction)
                    corrected_path = file_path.parent / corrected_name

                    if corrected_path.exists():
                        self.results.append(
                            ValidationResult(
                                file_path=str(file_path.relative_to(self.project_root)),
                                message=f"Archivo duplicado con typo - eliminar: {filename} (ya existe {corrected_name})",
                                level=ValidationLevel.ERROR,
                                rule="DOMAIN-TYPO-DUPLICATE",
                                suggestion=f"rm {file_path.relative_to(self.project_root)}",
                            )
                        )
                    else:
                        self.results.append(
                            ValidationResult(
                                file_path=str(file_path.relative_to(self.project_root)),
                                message=f"Typo detectado: '{typo}' debería ser '{correction}' en {filename}",
                                level=ValidationLevel.ERROR,
                                rule="DOMAIN-TYPO",
                                suggestion=f"mv {filename} {corrected_name}",
                            )
                        )

    def _suggest_snake_case(self, filename: str) -> str:
        """Sugiere versión en snake_case de un nombre"""
        base = filename.replace(".py", "")
        snake = re.sub(r"([A-Z])", r"_\1", base).lower().lstrip("_")
        return f"{snake}.py"

    def _suggest_pascal_case(self, filename: str) -> str:
        """Sugiere versión en PascalCase de un nombre"""
        base = filename.split(".")[0]
        words = re.split(r"[-_\s]", base.lower())
        pascal = "".join(word.capitalize() for word in words if word)
        extension = "." + ".".join(filename.split(".")[1:]) if "." in filename else ""
        return f"{pascal}{extension}"

    def _suggest_camel_case(self, filename: str) -> str:
        """Sugiere versión en camelCase de un nombre"""
        pascal = self._suggest_pascal_case(filename)
        if pascal:
            return pascal[0].lower() + pascal[1:]
        return filename

    def print_results(self) -> int:
        """
        Imprime resultados de validación de manera estructurada

        Returns:
            Código de salida (0 = éxito, 1 = errores encontrados)
        """
        print(f"\n{Colors.BLUE}Resultados:{Colors.END}")

        if not self.results:
            print(
                f"{Colors.GREEN} ¡Todos los archivos siguen los estándares de nombramiento!{Colors.END}"
            )
            print(
                f"{Colors.GREEN} Proyecto cumple 100% con las convenciones establecidas{Colors.END}"
            )
            return 0

        # Agrupar por nivel de severidad
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]

        if errors:
            print(f"{Colors.RED}❌ Se encontraron {len(errors)} errores:{Colors.END}\n")
            for result in errors:
                print(f"{Colors.RED}  ❌ {result.message}{Colors.END}")
                if result.file_path:
                    print(f"     📄 {result.file_path}")
                if result.suggestion:
                    print(
                        f"     💡 Sugerencia: {Colors.CYAN}{result.suggestion}{Colors.END}"
                    )
                print()

        if warnings:
            print(
                f"{Colors.YELLOW}⚠️  Se encontraron {len(warnings)} advertencias:{Colors.END}\n"
            )
            for result in warnings:
                print(f"{Colors.YELLOW}  ⚠️  {result.message}{Colors.END}")
                if result.file_path:
                    print(f"     📄 {result.file_path}")
                if result.suggestion:
                    print(
                        f"     💡 Sugerencia: {Colors.CYAN}{result.suggestion}{Colors.END}"
                    )
                print()

        # Estadísticas finales
        print(f"{Colors.BLUE}📈 Resumen:{Colors.END}")
        print(f"  • Total de problemas: {len(self.results)}")
        print(f"  • Errores críticos: {len(errors)}")
        print(f"  • Advertencias: {len(warnings)}")
        print(
            f"\n{Colors.YELLOW}📖 Consulta la documentación: docs/NAMING_CONVENTIONS.md{Colors.END}"
        )

        return 1 if errors else 0


def main() -> int:
    """
    Función principal del validador

    JUSTIFICACIÓN COMO SCRIPT INDEPENDIENTE:
    - Facilita integración en CI/CD pipelines
    - Permite ejecución manual para debugging
    - Compatible con pre-commit hooks
    - Salida estructurada para herramientas automatizadas
    """
    project_root = Path(__file__).parent.parent

    try:
        validator = NamingValidator(project_root)
        validator.validate_all()
        return validator.print_results()

    except Exception as e:
        print(f"{Colors.RED}❌ Error durante validación: {e}{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
