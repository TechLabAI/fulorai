import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyNavigationComponent } from './jrny-navigation.component';

describe('JrnyNavigationComponent', () => {
  let component: JrnyNavigationComponent;
  let fixture: ComponentFixture<JrnyNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
