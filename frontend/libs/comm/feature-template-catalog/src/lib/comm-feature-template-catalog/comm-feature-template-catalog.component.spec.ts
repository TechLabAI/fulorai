import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommFeatureTemplateCatalogComponent } from './comm-feature-template-catalog.component';

describe('CommFeatureTemplateCatalogComponent', () => {
  let component: CommFeatureTemplateCatalogComponent;
  let fixture: ComponentFixture<CommFeatureTemplateCatalogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommFeatureTemplateCatalogComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommFeatureTemplateCatalogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
